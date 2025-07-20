#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <curses.h>

#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>

#include <fstream>
#include <iostream>
#include <stack>
#include <vector>

#define MIN_HEIGHT    4
#define MIN_WIDTH    16
#define MAX_HEIGHT 1024
#define MAX_WIDTH  1024

#define STD_HEIGHT ((LINES - 6) / 1)
#define STD_WIDTH  ((COLS  - 3) / 2)

#define REC_RUL   2
#define REC_SPA   4
#define REC_OPN   8
#define REC_ERR 128

inline uint64_t msec() {
    struct timeval tv;
    gettimeofday(&tv, nullptr);
    return (uint64_t)tv.tv_sec * 1000 + tv.tv_usec / 1000;
}

class CellAuto {
    uint16_t h;
    uint16_t w;
    bool rule[2][9];

    struct Coordine {
        uint16_t x;
        uint16_t y;
    };

    Coordine ref;

    struct Relative {
        uint16_t x;
        uint16_t y;
    };

    struct Absolute {
        uint16_t x;
        uint16_t y;
    };

    Relative to_relative(Absolute const &abs) const {
        return {
            .x = (uint16_t)((abs.x + h - ref.x) % h),
            .y = (uint16_t)((abs.y + w - ref.y) % w),
        };
    }

    Absolute to_absolute(Relative const &rel) const {
        return {
            .x = (uint16_t)((rel.x + ref.x) % h),
            .y = (uint16_t)((rel.y + ref.y) % w),
        };
    }

    Absolute loc;

    struct Frame {
        std::vector<bool> cells;
    };

    auto set_cell_of(Frame &frame, Absolute const &abs) const {
        return frame.cells[abs.x * w + abs.y];
    }

    auto get_cell_of(Frame const &frame, Absolute const &abs) const {
        return frame.cells[abs.x * w + abs.y];
    }

    Frame new_frame() const {
        return Frame{std::vector<bool>(h * w)};
    }

    std::stack<Frame> undolog;
    std::stack<Frame> redolog;
    Frame current;

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

    static uint16_t valid_h(int h) {
        return h < MIN_HEIGHT ? MIN_HEIGHT : h > MAX_HEIGHT ? MAX_HEIGHT : h;
    }

    static uint16_t valid_w(int w) {
        return w < MIN_WIDTH  ? MIN_WIDTH  : w > MAX_WIDTH  ? MAX_WIDTH  : w;
    }

public:
    CellAuto(int h, int w)
        : h(valid_h(h))
        , w(valid_w(w))
        , rule{
            {0, 0, 0, 1, 0, 0, 0, 0, 0},
            {0, 0, 1, 1, 0, 0, 0, 0, 0},
        }
        , loc{0, 0}
        , ref{0, 0}
        , current(new_frame()) {}

    CellAuto(CellAuto const &) = delete;
    CellAuto(CellAuto &&) = default;

    CellAuto &operator=(CellAuto const &) = delete;
    CellAuto &operator=(CellAuto &&) = default;

    ~CellAuto() = default;

    void random_space(uint8_t d) {
        Frame next = new_frame();
        for (uint16_t i = 0; i < h; i++) {
            for (uint16_t j = 0; j < w; j++) {
                set_cell_of(next, {i, j}) = rand() % 8 < d;
            }
        }
        set_generation(std::move(next), true);
    }

    void move_ref(int16_t d, int16_t r) {
        ref.x = (ref.x + h + d) % h;
        ref.y = (ref.y + w + r) % w;
    }

    void move_loc(int16_t d, int16_t r) {
        loc.x = (loc.x + h + d) % h;
        loc.y = (loc.y + w + r) % w;
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

    void flip_cell() {
        Frame next = current;
        set_cell_of(next, loc).flip();
        set_generation(std::move(next));
    }

    void set_cell(bool n) {
        if (get_cell_of(current, loc) != n) {
            flip_cell();
        }
    }

    void step() {
        Frame next = new_frame();
        for (uint16_t i = 0; i < h; i++) {
            for (uint16_t j = 0; j < w; j++) {
                uint16_t u = i == 0 ? h - 1 : i - 1, d = i == h - 1 ? 0 : i + 1;
                uint16_t l = j == 0 ? w - 1 : j - 1, r = j == w - 1 ? 0 : j + 1;
                bool ul = get_cell_of(current, {u, l});
                bool uj = get_cell_of(current, {u, j});
                bool ur = get_cell_of(current, {u, r});
                bool il = get_cell_of(current, {i, l});
                bool ij = get_cell_of(current, {i, j});
                bool ir = get_cell_of(current, {i, r});
                bool dl = get_cell_of(current, {d, l});
                bool dj = get_cell_of(current, {d, j});
                bool dr = get_cell_of(current, {d, r});
                set_cell_of(next, {i, j}) = rule[ij][ul + uj + ur + il + ir + dl + dj + dr];
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

    bool get_cell(Relative rel) const {
        return get_cell_of(current, to_absolute(rel));
    }

    Relative get_loc() const {
        return to_relative(loc);
    }

    auto get_w() const {
        return w;
    }

    auto get_h() const {
        return h;
    }

    auto get_undonum() const {
        return undolog.size();
    }

    auto get_redonum() const {
        return redolog.size();
    }

    template<typename... Args>
    void save(Args &&...args) const {
        std::ofstream file(std::forward<Args>(args)...);
        if (file.fail()) {
            throw std::runtime_error("Failed to open file for saving");
        }
        file << h << ' ' << w << ' ' << get_rule() << std::endl;
        for (uint16_t i = 0; i < h; i++) {
            for (uint16_t j = 0; j < w; j++) {
                file << get_cell({i, j});
            }
            file << std::endl;
        }
    }

    template<typename... Args>
    static CellAuto open(Args &&...args) {
        std::ifstream file(std::forward<Args>(args)...);
        if (file.fail()) {
            throw std::runtime_error("Failed to open file");
        }
        int h, w;
        std::string rule_str;
        file >> h >> w;
        if (valid_h(h) != h || valid_w(w) != w) {
            throw std::runtime_error("Invalid height or width");
        }
        CellAuto ca(h, w);
        file >> rule_str;
        ca.set_rule(rule_str);
        for (uint16_t i = 0; i < h; i++) {
            std::string line;
            file >> line;
            if (line.size() != w) {
                throw std::runtime_error("Invalid line length in file");
            }
            for (uint16_t j = 0; j < w; j++) {
                ca.set_cell_of(ca.current, {i, j}) = line[j] == '1';
            }
        }
        return ca;
    }
};

void game(CellAuto const &ca, uint64_t interval, bool rand, bool play) {
    uint16_t top = std::max<int16_t>((STD_HEIGHT - ca.get_h()) / 2, 0);
    uint16_t left = std::max<int16_t>((STD_WIDTH - ca.get_w()) / 1, 0);
    uint32_t population = 0;
    WINDOW *info = newwin(3, 2 * ca.get_w() - 3, top, left);
    WINDOW *state = newwin(3, 6, top, 2 * ca.get_w() - 3 + left);
    WINDOW *space = newwin(ca.get_h() + 2, 2 * ca.get_w() + 3, top + 3, left);
    WINDOW *gen = newwin(1, 2 * ca.get_w() + 3, ca.get_h() + 5 + top, left);
    box(state, ACS_VLINE, ACS_HLINE);
    box(space, ACS_VLINE, ACS_HLINE);
    wattron(space, COLOR_PAIR(3));
    for (uint16_t i = 0; i < ca.get_h(); i++) {
        for (uint16_t j = 0; j < ca.get_w(); j++) {
            char c = ' ';
            if (ca.get_cell({i, j})) {
                c = '+';
                population++;
            }
            mvwaddch(space, i + 1, j * 2 + 2, c);
        }
    }
    wattroff(space, COLOR_PAIR(3));
    if (play) {
        wattron(state, COLOR_PAIR(2));
        mvwaddstr(state, 1, 2, "|>");
        wattroff(state, COLOR_PAIR(2));
    } else {
        wattron(state, COLOR_PAIR(1));
        mvwaddstr(state, 1, 2, "||");
        wattroff(state, COLOR_PAIR(1));
        auto [x, y] = ca.get_loc();
        mvwaddch(space, x + 1, y * 2 + 1, '>');
        mvwaddch(space, x + 1, y * 2 + 3, '<');
    }
    mvwprintw(info, 0, 0, "Rule = %s", ca.get_rule().c_str());
    mvwprintw(info, 1, 0, "Speed = %.2f", 1024.0 / interval);
    mvwprintw(info, 2, 0, "Undo/Redo = %lu/%lu", ca.get_undonum(), ca.get_redonum());
    mvwprintw(gen, 0, 0, "%*s%04d", 2 * ca.get_w() - 1, "Population = ", population);
    if (rand) {
        mvwprintw(gen, 0, 0, "Random...");
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

void menu(bool quit) {
    uint16_t top = std::max<int16_t>((LINES - 10) / 2, 0);
    uint16_t left = std::max<int16_t>((COLS - 18) / 2, 0);
    WINDOW *menu = newwin(10, 18, top, left);
    box(menu, ACS_VLINE, ACS_HLINE);
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
    if (quit) {
        WINDOW *exit = newwin(5, 18, top + 2, left);
        box(exit, ACS_VLINE, ACS_HLINE);
        mvwaddstr(exit, 0, 6, " Quit ");
        mvwaddstr(exit, 2, 1, "[Y]          Yes");
        mvwaddstr(exit, 3, 1, "[N]           No");
        wrefresh(exit);
        delwin(exit);
    }
    delwin(menu);
}

CellAuto parse(int argc, char *argv[]) {
    int rec = 0, h, w;
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
    if ((rec & REC_SPA) == 0) {
        h = STD_HEIGHT;
        w = STD_WIDTH;
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

    WINDOW *win = initscr();

    CellAuto ca = parse(argc, argv);

    noecho();
    curs_set(0);
    start_color();
    use_default_colors();
    init_pair(1, COLOR_RED, -1);
    init_pair(2, COLOR_GREEN, -1);
    init_pair(3, COLOR_YELLOW, -1);
    uint64_t interval = 1024, recd, next;

GAME_INIT:
    game(ca, interval, 0, 0);

GAME_REPT:
    switch (auto c = getch(); c) {
    case '-':
        interval = std::min<uint64_t>(interval * 2, 4096);
        goto GAME_INIT;
    case '=':
        interval = std::max<uint64_t>(interval / 2, 1);
        goto GAME_INIT;
    case '`':
        ca.step();
        goto GAME_INIT;
    case ',':
        ca.undo();
        goto GAME_INIT;
    case '.':
        ca.redo();
        goto GAME_INIT;
    case '<':
        while (ca.undo()) {}
        goto GAME_INIT;
    case '>':
        while (ca.redo()) {}
        goto GAME_INIT;
    case 'c':
        ca.random_space(0);
        goto GAME_INIT;
    case 'r':
        ca.random_space(2);
        goto GAME_INIT;
    case '0':
        ca.set_cell(0);
        goto GAME_INIT;
    case '1':
        ca.set_cell(1);
        goto GAME_INIT;
    case '*':
        ca.flip_cell();
        goto GAME_INIT;
    case 'w':
        ca.move_loc(-1, 0);
        goto GAME_INIT;
    case 'a':
        ca.move_loc(0, -1);
        goto GAME_INIT;
    case 's':
        ca.move_loc(+1, 0);
        goto GAME_INIT;
    case 'd':
        ca.move_loc(0, +1);
        goto GAME_INIT;
    case 'W':
        ca.move_ref(-1, 0);
        goto GAME_INIT;
    case 'A':
        ca.move_ref(0, -1);
        goto GAME_INIT;
    case 'S':
        ca.move_ref(+1, 0);
        goto GAME_INIT;
    case 'D':
        ca.move_ref(0, +1);
        goto GAME_INIT;
    case 'R':
        goto RAND_INIT;
    case ' ':
        recd = msec();
        goto PLAY_INIT;
    case 'm':
        clear();
        goto MENU_INIT;
    case KEY_RESIZE:
        clear();
        goto GAME_INIT;
    default:
        goto GAME_REPT;
    }

RAND_INIT:
    game(ca, interval, 1, 0);

RAND_REPT:
    switch (auto c = getch(); c) {
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
        goto GAME_INIT;
    case KEY_RESIZE:
        clear();
        goto RAND_INIT;
    default:
        goto RAND_REPT;
    }

PLAY_INIT:
    game(ca, interval, 0, 1);

PLAY_REPT:
    timeout(std::max<int64_t>((next = recd + interval) - msec(), 0));
    switch (auto c = getch(); c) {
    case '-':
        interval = std::min<uint64_t>(interval * 2, 4096);
        goto PLAY_INIT;
    case '=':
        interval = std::max<uint64_t>(interval / 2, 1);
        goto PLAY_INIT;
    case 'W':
        ca.move_ref(-1, 0);
        goto PLAY_INIT;
    case 'A':
        ca.move_ref(0, -1);
        goto PLAY_INIT;
    case 'S':
        ca.move_ref(+1, 0);
        goto PLAY_INIT;
    case 'D':
        ca.move_ref(0, +1);
        goto PLAY_INIT;
    case ' ':
        timeout(-1);
        goto GAME_INIT;
    case KEY_RESIZE:
        clear();
        goto PLAY_INIT;
    case ERR:  // timeout
        ca.step();
        recd = next;
        goto PLAY_INIT;
    default:
        goto PLAY_REPT;
    }

MENU_INIT:
    menu(0);

MENU_REPT:
    switch (getch()) {
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
        if (success) {
            goto GAME_INIT;
        } else {
            goto MENU_INIT;
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
        if (success) {
            goto GAME_INIT;
        } else {
            goto MENU_INIT;
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
        reset_prog_mode();
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
        if (success) {
            goto GAME_INIT;
        } else {
            goto MENU_INIT;
        }
    }
    case 'z': {
        def_prog_mode();
        endwin();
        int h, w;
        std::cout << ">> Height: ";
        while ((std::cin >> h).fail()) {
            std::cin.clear();
        }
        std::cout << ">> Width: ";
        while ((std::cin >> w).fail()) {
            std::cin.clear();
        }
        reset_prog_mode();
        auto rule_str = ca.get_rule();
        ca = CellAuto(h, w);
        ca.set_rule(rule_str);
        goto GAME_INIT;
    }
    case 'a': {
        auto rule_str = ca.get_rule();
        ca = CellAuto(STD_HEIGHT, STD_WIDTH);
        ca.set_rule(rule_str);
        goto GAME_INIT;
    }
    case 'c':
        goto GAME_INIT;
    case 'q':
        goto QUIT_INIT;
    case KEY_RESIZE:
        clear();
        goto MENU_INIT;
    default:
        goto MENU_REPT;
    }

QUIT_INIT:
    menu(1);

QUIT_REPT:
    switch (getch()) {
    case 'y':
        endwin();
        return 0;
    case 'n':
        goto MENU_INIT;
    case KEY_RESIZE:
        clear();
        goto QUIT_INIT;
    default:
        goto QUIT_REPT;
    }
}
