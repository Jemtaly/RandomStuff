#include <unistd.h>
#include <curses.h>

#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>

#include <fstream>
#include <iostream>
#include <stack>
#include <unordered_set>
#include <unordered_map>
#include <chrono>

#define REC_RUL   2
#define REC_SPA   4
#define REC_OPN   8
#define REC_ERR 128

typedef int64_t msec_t;

typedef uint16_t absolute_t;
typedef int64_t relative_t;

inline msec_t msec() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
}

struct Absolute {
    absolute_t x;
    absolute_t y;
};

inline bool operator==(Absolute const &a, Absolute const &b) {
    return a.x == b.x && a.y == b.y;
}

template<>
struct std::hash<Absolute> {
    std::size_t operator()(Absolute const &abs) const noexcept {
        return std::hash<absolute_t>()(abs.x) ^ std::hash<absolute_t>()(abs.y) << 1;
    }
};

struct Relative {
    relative_t x;
    relative_t y;
};

struct Frame {
    bool base = false;
    std::unordered_set<Absolute> revs;
};

class CellAuto {
    absolute_t h;
    absolute_t w;
    bool rule[2][9];

    std::stack<Frame> undolog;
    std::stack<Frame> redolog;
    Frame current;

    Frame new_frame() const {
        return Frame();
    }

    Absolute to_absolute(Relative rel) const {
        relative_t x = rel.x % (h == 0 ? ((relative_t)std::numeric_limits<absolute_t>::max() + 1) : (relative_t)h);
        relative_t y = rel.y % (w == 0 ? ((relative_t)std::numeric_limits<absolute_t>::max() + 1) : (relative_t)w);
        return {
            .x = static_cast<absolute_t>(x < 0 ? x + h : x),
            .y = static_cast<absolute_t>(y < 0 ? y + w : y),
        };
    }

    void clear_undolog() {
        while (!undolog.empty()) {
            undolog.pop();
        }
    }

    void clear_redolog() {
        while (!redolog.empty()) {
            redolog.pop();
        }
    }

    void set_generation(Frame &&next, bool init = false) {
        clear_redolog();
        if (init) {
            clear_undolog();
        } else {
            undolog.push(std::move(current));
        }
        current = std::move(next);
    }

public:
    CellAuto(absolute_t h, absolute_t w)
        : w(w)
        , h(h)
        , rule{
            {0, 0, 0, 1, 0, 0, 0, 0, 0},
            {0, 0, 1, 1, 0, 0, 0, 0, 0},
        }
        , current(new_frame()) {}

    CellAuto(CellAuto const &) = delete;
    CellAuto(CellAuto &&) = default;

    CellAuto &operator=(CellAuto const &) = delete;
    CellAuto &operator=(CellAuto &&) = default;

    ~CellAuto() = default;

    void random_space(uint8_t d) {
        Frame next = new_frame();
        if (d == 0) {
            next.base = 0;
        } else if (d >= 8) {
            next.base = 1;
        } else if (h > 0 && w > 0) {
            for (absolute_t i = 0; i < h; ++i) {
                for (absolute_t j = 0; j < w; ++j) {
                    if (rand() % 8 < d) {
                        next.revs.insert({
                            .x = i,
                            .y = j,
                        });
                    }
                }
            }
        }
        set_generation(std::move(next), true);
    }

    void set_rule(std::string_view rule_str) {
        bool new_rule[2][9] = {};
        for (bool i = 0; auto r : rule_str) {
            switch (r) {
            case 'b':
            case 'B':
                i = 0;
                break;
            case 's':
            case 'S':
                i = 1;
                break;
            case '/':
                i ^= 1;
                break;
            default:
                if (r >= '0' && r < '9') {
                    new_rule[i][r - '0'] = 1;
                } else {
                    throw std::runtime_error("Invalid rule character: " + std::string(1, r));
                }
            }
        }
        for (int i = 0; i < 9; i++) {
            this->rule[0][i] = new_rule[0][i];
            this->rule[1][i] = new_rule[1][i];
        }
    }

    auto get_rule() const {
        std::string b_str = "B";
        for (int i = 0; i < 9; i++) {
            if (this->rule[0][i]) {
                b_str += char('0' + i);
            }
        }
        std::string s_str = "S";
        for (int i = 0; i < 9; i++) {
            if (this->rule[1][i]) {
                s_str += char('0' + i);
            }
        }
        return b_str + '/' + s_str;
    }

    void flip_base() {
        Frame next = current;
        next.base = !next.base;
        set_generation(std::move(next));
    }

    void flip_cell(Relative loc) {
        Absolute abs = to_absolute(loc);
        Frame next = current;
        if (next.revs.count(abs)) {
            next.revs.erase(abs);
        } else {
            next.revs.insert(abs);
        }
        set_generation(std::move(next));
    }

    void set_cell(Relative loc, bool alive) {
        Absolute abs = to_absolute(loc);
        bool target = current.base != alive;
        if (target & !current.revs.count(abs)) {
            Frame next = current;
            next.revs.insert(abs);
            set_generation(std::move(next));
        }
        if (!target && current.revs.count(abs)) {
            Frame next = current;
            next.revs.erase(abs);
            set_generation(std::move(next));
        }
    }

    bool get_cell(Relative loc) const {
        return current.base ^ current.revs.count(to_absolute(loc));
    }

    void step() {
        std::unordered_map<Absolute, std::pair<bool, uint8_t>> specials;
        for (auto [x, y] : current.revs) {
            for (int dx = -1; dx <= 1; ++dx) {
                for (int dy = -1; dy <= 1; ++dy) {
                    Absolute pos = {
                        .x = static_cast<absolute_t>(dx < 0 && x == 0 ? h - 1 : (dx > 0 && x == h - 1 ? 0 : x + dx)),
                        .y = static_cast<absolute_t>(dy < 0 && y == 0 ? w - 1 : (dy > 0 && y == w - 1 ? 0 : y + dy)),
                    };
                    if (dx == 0 && dy == 0) {
                        specials[pos].first = true;
                    } else {
                        specials[pos].second++;
                    }
                }
            }
        }
        Frame next = new_frame();
        next.base = rule[current.base][current.base ? 8 : 0];
        for (auto [abs, info] : specials) {
            if (rule[current.base ^ info.first][current.base ? 8 - info.second : info.second] != next.base) {
                next.revs.insert(abs);
            }
        }
        set_generation(std::move(next));
    }

    bool undo() {
        if (undolog.empty()) {
            return 0;
        }
        redolog.push(std::move(current));
        current = std::move(undolog.top());
        undolog.pop();
        return 1;
    }

    bool redo() {
        if (redolog.empty()) {
            return 0;
        }
        undolog.push(std::move(current));
        current = std::move(redolog.top());
        redolog.pop();
        return 1;
    }

    auto get_undonum() const {
        return undolog.size();
    }

    auto get_redonum() const {
        return redolog.size();
    }

    size_t population() const {
        if (current.base) {
            size_t real_h = h == 0 ? std::numeric_limits<absolute_t>::max() : h;
            size_t real_w = w == 0 ? std::numeric_limits<absolute_t>::max() : w;
            return real_h * real_w - current.revs.size();
        } else {
            return current.revs.size();
        }
    }

    template<typename... Args>
    void save(Args &&...args) const {
        std::ofstream file(std::forward<Args>(args)...);
        if (file.fail()) {
            throw std::runtime_error("Failed to open file for saving");
        }

        file << h << ' ' << w << std::endl;
        if (file.fail()) {
            throw std::runtime_error("Failed to write dimensions");
        }

        file << current.base << std::endl;
        if (file.fail()) {
            throw std::runtime_error("Failed to write base state");
        }

        file << current.revs.size() << std::endl;
        if (file.fail()) {
            throw std::runtime_error("Failed to write cell count");
        }
        for (const auto &cell : current.revs) {
            file << cell.x << ' ' << cell.y << std::endl;
            if (file.fail()) {
                throw std::runtime_error("Failed to write cell data");
            }
        }

        file << get_rule() << std::endl;
        if (file.fail()) {
            throw std::runtime_error("Failed to write rule data");
        }
    }

    template<typename... Args>
    static CellAuto open(Args &&...args) {
        std::ifstream file(std::forward<Args>(args)...);
        if (file.fail()) {
            throw std::runtime_error("Failed to open file");
        }

        absolute_t h, w;
        file >> h >> w;
        if (file.fail()) {
            throw std::runtime_error("Failed to read dimensions");
        }
        CellAuto ca(h, w);

        bool base;
        file >> base;
        if (file.fail()) {
            throw std::runtime_error("Failed to read base state");
        }
        ca.current.base = base;

        size_t cell_count;
        file >> cell_count;
        if (file.fail()) {
            throw std::runtime_error("Failed to read dimensions or cell count");
        }
        for (size_t i = 0; i < cell_count; ++i) {
            Absolute abs;
            file >> abs.x >> abs.y;
            if (file.fail()) {
                throw std::runtime_error("Failed to read cell data");
            }
            ca.current.revs.insert(abs);
        }

        std::string rule_str;
        file >> rule_str;
        if (file.fail()) {
            throw std::runtime_error("Failed to read rule data");
        }
        ca.set_rule(rule_str);

        return ca;
    }
};

struct Screen {
    int h;
    int w;
};

void adjust_loc(Screen const &screen, Relative const &ref, Relative &loc) {
    if (loc.x < ref.x) { loc.x = ref.x; } else if (loc.x >= ref.x + screen.h) { loc.x = ref.x + screen.h - 1; }
    if (loc.y < ref.y) { loc.y = ref.y; } else if (loc.y >= ref.y + screen.w) { loc.y = ref.y + screen.w - 1; }
}

void adjust_ref(Screen const &screen, Relative const &loc, Relative &ref) {
    if (loc.x < ref.x) { ref.x = loc.x; } else if (loc.x >= ref.x + screen.h) { ref.x = loc.x - screen.h + 1; }
    if (loc.y < ref.y) { ref.y = loc.y; } else if (loc.y >= ref.y + screen.w) { ref.y = loc.y - screen.w + 1; }
}

void move_loc(Screen const &screen, Relative &loc, Relative &ref, relative_t dx, relative_t dy) {
    loc.x += dx;
    loc.y += dy;
    adjust_ref(screen, loc, ref);
}

void move_ref(Screen const &screen, Relative &ref, Relative &loc, relative_t dx, relative_t dy) {
    ref.x += dx;
    ref.y += dy;
    adjust_loc(screen, ref, loc);
}

void box(WINDOW *win) {
    cchar_t l_, r_, _t, _b, tl, tr, bl, br;
    setcchar(&l_, L"│", A_NORMAL, 0, NULL);
    setcchar(&r_, L"│", A_NORMAL, 0, NULL);
    setcchar(&_t, L"─", A_NORMAL, 0, NULL);
    setcchar(&_b, L"─", A_NORMAL, 0, NULL);
    setcchar(&tl, L"╭", A_NORMAL, 0, NULL);
    setcchar(&tr, L"╮", A_NORMAL, 0, NULL);
    setcchar(&bl, L"╰", A_NORMAL, 0, NULL);
    setcchar(&br, L"╯", A_NORMAL, 0, NULL);
    wborder_set(win, &l_, &r_, &_t, &_b, &tl, &tr, &bl, &br);
}

void game(CellAuto const &ca, Screen &screen, Relative &ref, Relative &loc, msec_t interval, bool rand, bool play) {
    int lines = std::max<int>(LINES, 10);
    int cols  = std::max<int>(COLS,  18);
    screen.h = ((lines - 6) / 1);
    screen.w = ((cols  - 3) / 2);
    adjust_ref(screen, loc, ref);

    WINDOW *info = newwin(3, cols - 6, 0, 0);
    mvwprintw(info, 0, 0, "Rule = %s", ca.get_rule().c_str());
    mvwprintw(info, 1, 0, "Speed = %.2f", 1024.0 / interval);
    mvwprintw(info, 2, 0, "Undo/Redo = %lu/%lu", ca.get_undonum(), ca.get_redonum());

    WINDOW *space = newwin(lines - 4, cols, 3, 0);
    box(space);
    wattron(space, COLOR_PAIR(3));
    for (int i = 0; i < screen.h; i++) {
        for (int j = 0; j < screen.w; j++) {
            mvwaddch(space, i + 1, j * 2 + 2, ca.get_cell({ref.x + i, ref.y + j}) ? '+' : ' ');
        }
    }
    wattroff(space, COLOR_PAIR(3));
    if (not play) {
        int x = loc.x - ref.x;
        int y = loc.y - ref.y;
        mvwaddch(space, x + 1, y * 2 + 2 - 1, '>');
        mvwaddch(space, x + 1, y * 2 + 2 + 1, '<');
    }

    WINDOW *state = newwin(3, 6, 0, cols - 6);
    box(state);
    if (play) {
        wattron(state, COLOR_PAIR(2));
        mvwaddstr(state, 1, 2, "|>");
        wattroff(state, COLOR_PAIR(2));
    } else {
        wattron(state, COLOR_PAIR(1));
        mvwaddstr(state, 1, 2, "||");
        wattroff(state, COLOR_PAIR(1));
    }

    WINDOW *gen = newwin(1, cols, lines - 1, 0);
    mvwprintw(gen, 0, 0, "Population = %zu", ca.population());
    if (rand) {
        mvwprintw(gen, 0, cols - 9, "Random...");
    }

    refresh();
    wrefresh(info);
    wrefresh(state);
    wrefresh(space);
    wrefresh(gen);
    delwin(info);
    delwin(state);
    delwin(space);
    delwin(gen);
}

void menu() {
    int top = std::max<int>((LINES - 10) / 2, 0);
    int left = std::max<int>((COLS - 18) / 2, 0);
    WINDOW *menu = newwin(10, 18, top, left);
    box(menu);
    mvwaddstr(menu, 0, 6, " Menu ");
    mvwaddstr(menu, 2, 1, "[O]         Open");
    mvwaddstr(menu, 3, 1, "[S]         Save");
    mvwaddstr(menu, 4, 1, "[R]     Set Rule");
    mvwaddstr(menu, 5, 1, "[Z]       Resize");
    mvwaddstr(menu, 6, 1, "[A]  Auto Resize");
    mvwaddstr(menu, 7, 1, "[C]     Continue");
    mvwaddstr(menu, 8, 1, "[Q]         Quit");
    refresh();
    wrefresh(menu);
    delwin(menu);
}

void quit() {
    int top = std::max<int>((LINES -  5) / 2, 0);
    int left = std::max<int>((COLS - 18) / 2, 0);
    WINDOW *exit = newwin(5, 18, top, left);
    box(exit);
    mvwaddstr(exit, 0, 6, " Quit ");
    mvwaddstr(exit, 2, 1, "[Y]          Yes");
    mvwaddstr(exit, 3, 1, "[N]           No");
    refresh();
    wrefresh(exit);
    delwin(exit);
}

CellAuto parse(int argc, char *argv[]) {
    int rec = 0;
    absolute_t h = 0;
    absolute_t w = 0;
    char* rule_str = nullptr;
    char* filename = nullptr;
    for (int i = 1; (rec & REC_ERR) == 0 && i < argc; i++) {
        if (argv[i][0] != '-') {
            if ((rec & (REC_RUL | REC_SPA | REC_OPN)) == 0) {
                filename = argv[i];
                rec |= REC_OPN;
            } else {
                rec |= REC_ERR;
            }
        } else if (argv[i][1] == 'r' && argv[i][2] == '\0') {
            if ((rec & (REC_OPN | REC_RUL)) == 0 && i + 1 < argc) {
                rule_str = argv[++i];
                rec |= REC_RUL;
            } else {
                rec |= REC_ERR;
            }
        } else if (argv[i][1] == 'n' && argv[i][2] == '\0') {
            if ((rec & (REC_SPA | REC_OPN)) == 0 && i + 2 < argc) {
                h = atoi(argv[++i]);
                w = atoi(argv[++i]);
                rec |= REC_SPA;
            } else {
                rec |= REC_ERR;
            }
        } else {
            rec |= REC_ERR;
        }
    }
    if ((rec & REC_ERR) != 0) {
        endwin();
        std::cerr << "Description: Conway's Game of Life" << std::endl
                  << "Usage: " << argv[0] << " [-b] [-r RULE] [-n H W] or " << argv[0] << " FILE" << std::endl
                  << "Options:" << std::endl
                  << "  FILE     open file" << std::endl
                  << "  -n H W   set height and width" << std::endl
                  << "  -r RULE  set rule" << std::endl;
        exit(1);
    }
    if ((rec & REC_OPN) != 0) {
        try {
            return CellAuto::open(filename);
        } catch (const std::runtime_error &e) {
            endwin();
            std::cerr << "Error: " << e.what() << std::endl;
            exit(1);
        }
    }
    auto ca = CellAuto(h, w);
    if ((rec & REC_RUL) != 0) {
        try {
            ca.set_rule(rule_str);
        } catch (const std::runtime_error &e) {
            endwin();
            std::cerr << "Error: " << e.what() << std::endl;
            exit(1);
        }
    }
    return ca;
}

int main(int argc, char *argv[]) {
    if (!isatty(fileno(stdin)) || !isatty(fileno(stdout))) {
        std::cerr << "Error: unsupported stdin/stdout" << std::endl;
        exit(1);
    }

    setlocale(LC_ALL, "");

    CellAuto ca = parse(argc, argv);
    Relative loc = {0, 0};
    Relative ref = {0, 0};

    WINDOW *win = initscr();
    noecho();
    curs_set(0);
    start_color();
    use_default_colors();
    init_pair(1, COLOR_RED, -1);
    init_pair(2, COLOR_GREEN, -1);
    init_pair(3, COLOR_YELLOW, -1);

    Screen screen;

    msec_t interval = 1024, last;

GAME_REFRESH:
    game(ca, screen, ref, loc, interval, 0, 0);

    for (;;) {
        auto c = getch();
        switch (c) {
        case '-':
            interval = std::min<msec_t>(interval * 2, 4096);
            goto GAME_REFRESH;
        case '=':
            interval = std::max<msec_t>(interval / 2, 1);
            goto GAME_REFRESH;
        case '`':
            ca.step();
            goto GAME_REFRESH;
        case ',':
            ca.undo();
            goto GAME_REFRESH;
        case '.':
            ca.redo();
            goto GAME_REFRESH;
        case '<':
            while (ca.undo()) {}
            goto GAME_REFRESH;
        case '>':
            while (ca.redo()) {}
            goto GAME_REFRESH;
        case 'c':
            ca.random_space(0);
            goto GAME_REFRESH;
        case 'r':
            ca.random_space(2);
            goto GAME_REFRESH;
        case '0':
            ca.set_cell(loc, 0);
            goto GAME_REFRESH;
        case '1':
            ca.set_cell(loc, 1);
            goto GAME_REFRESH;
        case '*':
            ca.flip_cell(loc);
            goto GAME_REFRESH;
        case '@':
            ca.flip_base();
            goto GAME_REFRESH;
        case 'w':
            move_loc(screen, loc, ref, -1, 0);
            goto GAME_REFRESH;
        case 'a':
            move_loc(screen, loc, ref, 0, -1);
            goto GAME_REFRESH;
        case 's':
            move_loc(screen, loc, ref, +1, 0);
            goto GAME_REFRESH;
        case 'd':
            move_loc(screen, loc, ref, 0, +1);
            goto GAME_REFRESH;
        case 'W':
            move_ref(screen, ref, loc, -1, 0);
            goto GAME_REFRESH;
        case 'A':
            move_ref(screen, ref, loc, 0, -1);
            goto GAME_REFRESH;
        case 'S':
            move_ref(screen, ref, loc, +1, 0);
            goto GAME_REFRESH;
        case 'D':
            move_ref(screen, ref, loc, 0, +1);
            goto GAME_REFRESH;
        case 'R':
            clear();
            goto RAND_REFRESH;
        case ' ':
            clear();
            goto PLAY_START;
        case 'm':
            clear();
            goto MENU_REFRESH;
        case KEY_RESIZE:
            clear();
            goto GAME_REFRESH;
        }
    }

RAND_REFRESH:
    game(ca, screen, ref, loc, interval, 1, 0);

    for (;;) {
        auto c = getch();
        switch (c) {
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
            ca.random_space(c - '0');
            clear();
            goto GAME_REFRESH;
        case KEY_RESIZE:
            clear();
            goto RAND_REFRESH;
        }
    }

PLAY_START:
    last = msec();

PLAY_REFRESH:
    game(ca, screen, ref, loc, interval, 0, 1);

    for (;;) {
        msec_t next = last + interval;
        msec_t time = std::max<msec_t>(next - msec(), 0);
        timeout(time);
        auto c = getch();
        timeout(-1);
        switch (c) {
        case ERR:  // timeout
            ca.step();
            last = next;
            goto PLAY_REFRESH;
        case '-':
            interval = std::min<msec_t>(interval * 2, 4096);
            goto PLAY_REFRESH;
        case '=':
            interval = std::max<msec_t>(interval / 2, 1);
            goto PLAY_REFRESH;
        case 'W':
            move_ref(screen, ref, loc, -1, 0);
            goto PLAY_REFRESH;
        case 'A':
            move_ref(screen, ref, loc, 0, -1);
            goto PLAY_REFRESH;
        case 'S':
            move_ref(screen, ref, loc, +1, 0);
            goto PLAY_REFRESH;
        case 'D':
            move_ref(screen, ref, loc, 0, +1);
            goto PLAY_REFRESH;
        case ' ':
            clear();
            goto GAME_REFRESH;
        case KEY_RESIZE:
            clear();
            goto PLAY_REFRESH;
        }
    }

MENU_REFRESH:
    game(ca, screen, ref, loc, interval, 0, 0);
    menu();

    for (;;) {
        auto c = getch();
        switch (c) {
        case 'o': {
            def_prog_mode();
            endwin();
            std::string filename;
            std::cout << ">> Filename: ";
            while ((std::cin >> filename).fail()) {
                std::cin.clear();
            }
            bool success = false;
            try {
                ca = CellAuto::open(filename);
                success = true;
                std::cout << "=> File opened successfully!" << std::endl;
            } catch (const std::runtime_error &e) {
                std::cout << "=> Error: " << e.what() << std::endl;
            }
            sleep(1);
            reset_prog_mode();
            clear();
            if (success) {
                goto GAME_REFRESH;
            } else {
                goto MENU_REFRESH;
            }
        }
        case 's': {
            def_prog_mode();
            endwin();
            std::string filename;
            std::cout << ">> Filename: ";
            while ((std::cin >> filename).fail()) {
                std::cin.clear();
            }
            bool success = false;
            try {
                ca.save(filename);
                success = true;
                std::cout << "=> File saved successfully!" << std::endl;
            } catch (const std::runtime_error &e) {
                std::cout << "=> Error: " << e.what() << std::endl;
            }
            sleep(1);
            reset_prog_mode();
            clear();
            if (success) {
                goto GAME_REFRESH;
            } else {
                goto MENU_REFRESH;
            }
        }
        case 'r': {
            def_prog_mode();
            endwin();
            std::string rule_str;
            std::cout << ">> Rule(B/S): ";
            while ((std::cin >> rule_str).fail()) {
                std::cin.clear();
            }
            bool success = false;
            try {
                ca.set_rule(rule_str);
                success = true;
                std::cout << "=> Rule set successfully!" << std::endl;
            } catch (const std::runtime_error &e) {
                std::cout << "=> Error: " << e.what() << std::endl;
            }
            sleep(1);
            reset_prog_mode();
            clear();
            if (success) {
                goto GAME_REFRESH;
            } else {
                goto MENU_REFRESH;
            }
        }
        case 'z': {
            def_prog_mode();
            endwin();
            absolute_t h = 0;
            std::cout << ">> Height: ";
            while ((std::cin >> h).fail()) {
                std::cin.clear();
            }
            absolute_t w = 0;
            std::cout << ">> Width: ";
            while ((std::cin >> w).fail()) {
                std::cin.clear();
            }
            reset_prog_mode();
            auto rule_str = ca.get_rule();
            ca = CellAuto(h, w);
            ca.set_rule(rule_str);
            clear();
            goto GAME_REFRESH;
        }
        case 'a': {
            absolute_t h = screen.h > std::numeric_limits<absolute_t>::max() ? 0 : screen.h;
            absolute_t w = screen.w > std::numeric_limits<absolute_t>::max() ? 0 : screen.w;
            auto rule_str = ca.get_rule();
            ca = CellAuto(h, w);
            ca.set_rule(rule_str);
            clear();
            goto GAME_REFRESH;
        }
        case 'c':
            clear();
            goto GAME_REFRESH;
        case 'q':
            clear();
            goto QUIT_REFRESH;
        case KEY_RESIZE:
            clear();
            goto MENU_REFRESH;
        }
    }

QUIT_REFRESH:
    game(ca, screen, ref, loc, interval, 0, 0);
    menu();
    quit();

    for (;;) {
        auto c = getch();
        switch (c) {
        case 'y':
            clear();
            goto END;
        case 'n':
            clear();
            goto MENU_REFRESH;
        case KEY_RESIZE:
            clear();
            goto QUIT_REFRESH;
        }
    }

END:
    endwin();
    return 0;
}
