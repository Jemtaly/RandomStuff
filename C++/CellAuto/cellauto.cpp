#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>
#include <fstream>
#include <iostream>
#include <stack>
#include "curses.h"
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MIN_HEIGHT 4
#define MIN_WIDTH 16
#define MAX_HEIGHT 1024
#define MAX_WIDTH 1024
#define STD_HEIGHT (LINES - 6)
#define STD_WIDTH ((COLS - 3) / 2)
#define REC_MOD 1
#define REC_RUL 2
#define REC_SPA 4
#define REC_OPN 8
#define REC_ERR 128
uint64_t usec() {
    timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000000 + tv.tv_usec;
}
class CellAuto {
    uint16_t height, width;
    struct XY {
        uint16_t x, y;
    } location, reference;
    struct GenerationInfo {
        bool *space;
        bool rule[2][9];
        XY *bound;
        size_t generation;
    } current;
    std::stack<GenerationInfo> undolog, redolog;
    void clear_undolog() {
        for (auto bound = current.bound; !undolog.empty(); undolog.pop()) {
            delete[] undolog.top().space;
            if (auto rec = bound; (bound = undolog.top().bound) && !rec) {
                delete bound;
            }
        }
    }
    void clear_redolog() {
        for (auto bound = current.bound; !redolog.empty(); redolog.pop()) {
            delete[] redolog.top().space;
            if (auto rec = bound; (bound = redolog.top().bound) && !rec) {
                delete bound;
            }
        }
    }
    void init_generation(bool set) {
        clear_undolog();
        clear_redolog();
        if (set) {
            current.generation = 0;
        }
    }
    void copy_generation(bool set) {
        clear_redolog();
        auto space = new bool[height * width];
        memcpy(space, current.space, height * width);
        undolog.push(current);
        current.space = space;
        if (set) {
            current.generation++;
        }
    }
public:
    CellAuto(CellAuto const &) = delete;
    CellAuto &operator=(CellAuto const &) = delete;
    CellAuto(int h, int w):
        height(h < MIN_HEIGHT ? MIN_HEIGHT : h > MAX_HEIGHT ? MAX_HEIGHT : h),
        width(w < MIN_WIDTH ? MIN_WIDTH : w > MAX_WIDTH ? MAX_WIDTH : w),
        location{0, 0},
        reference{0, 0},
        current{new bool[height * width], {{0, 0, 0, 1, 0, 0, 0, 0, 0}, {0, 0, 1, 1, 0, 0, 0, 0, 0}}, nullptr, 0} {}
    ~CellAuto() {
        clear_undolog();
        clear_redolog();
        delete[] current.space;
        if (current.bound) {
            delete current.bound;
        }
    }
    void move_location(char dir) {
        switch (dir) {
        case 'w':
            if (!current.bound || location.x != reference.x) {
                location.x = (location.x + height - 1) % height;
            }
            break;
        case 's':
            if (!current.bound || location.x != (reference.x + height - 1) % height) {
                location.x = (location.x + 1) % height;
            }
            break;
        case 'a':
            if (!current.bound || location.y != reference.y) {
                location.y = (location.y + width - 1) % width;
            }
            break;
        case 'd':
            if (!current.bound || location.y != (reference.y + width - 1) % width) {
                location.y = (location.y + 1) % width;
            }
            break;
        }
    }
    void move_reference(char dir) {
        if (current.bound) {
            return;
        }
        move_location(dir);
        switch (dir) {
        case 'w':
            reference.x = (reference.x + height - 1) % height;
            break;
        case 's':
            reference.x = (reference.x + 1) % height;
            break;
        case 'a':
            reference.y = (reference.y + width - 1) % width;
            break;
        case 'd':
            reference.y = (reference.y + 1) % width;
            break;
        }
    }
    void reset_space(int h, int w) {
        init_generation(true);
        delete[] current.space;
        height = h < MIN_HEIGHT ? MIN_HEIGHT : h > MAX_HEIGHT ? MAX_HEIGHT : h;
        width = w < MIN_WIDTH ? MIN_WIDTH : w > MAX_WIDTH ? MAX_WIDTH : w;
        current.space = new bool[height * width];
        if (current.bound) {
            current.bound->x = current.bound->y = 0;
        }
        reference.x = reference.y = location.x = location.y = 0;
    }
    void random_space(uint8_t d) {
        init_generation(true);
        for (uint16_t i = 0; i < height; i++) {
            for (uint16_t j = 0; j < width; j++) {
                current.space[i * width + j] = rand() % 8 < d;
            }
        }
    }
    void set_rule(std::string const &rule) {
        bool new_rule[2][9] = {};
        for (bool i = 0; auto r : rule) {
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
                }
            }
        }
        bool changed = 0;
        for (int i = 0; i < 9; i++) {
            changed |= current.rule[0][i] != new_rule[0][i] || current.rule[1][i] != new_rule[1][i];
        }
        if (changed) {
            copy_generation(false);
            for (int i = 0; i < 9; i++) {
                current.rule[0][i] = new_rule[0][i];
                current.rule[1][i] = new_rule[1][i];
            }
        }
    }
    auto get_rule() const {
        std::string rule = "B";
        for (int i = 0; i < 9; i++) {
            if (current.rule[0][i]) {
                rule += char('0' + i);
            }
        }
        rule += "/S";
        for (int i = 0; i < 9; i++) {
            if (current.rule[1][i]) {
                rule += char('0' + i);
            }
        }
        return rule;
    }
    void switch_mode() {
        copy_generation(false);
        current.bound = current.bound ? nullptr : new XY(reference);
    }
    bool get_mode() const {
        return current.bound;
    }
    void switch_cell() {
        copy_generation(false);
        current.space[location.x * width + location.y] ^= 1;
    }
    void set_cell(bool n) {
        if (current.space[location.x * width + location.y] != n) {
            switch_cell();
        }
    }
    void step() {
        auto space = current.space;
        auto &next = current.space;
        copy_generation(true);
        for (uint16_t i = 0; i < height; i++) {
            for (uint16_t j = 0; j < width; j++) {
                uint16_t reference_x = reference.x == 0 ? height - 1 : reference.x - 1;
                uint16_t reference_y = reference.y == 0 ? width - 1 : reference.y - 1;
                uint16_t w = i == 0 ? height - 1 : i - 1, s = i == height - 1 ? 0 : i + 1;
                uint16_t a = j == 0 ? width - 1 : j - 1, d = j == width - 1 ? 0 : j + 1;
                bool wj = (!current.bound || i != reference.x) && space[w * width + j];
                bool sj = (!current.bound || i != reference_x) && space[s * width + j];
                bool ia = (!current.bound || j != reference.y) && space[i * width + a];
                bool id = (!current.bound || j != reference_y) && space[i * width + d];
                bool wa = (!current.bound || i != reference.x && j != reference.y) && space[w * width + a];
                bool wd = (!current.bound || i != reference.x && j != reference_y) && space[w * width + d];
                bool sa = (!current.bound || i != reference_x && j != reference.y) && space[s * width + a];
                bool sd = (!current.bound || i != reference_x && j != reference_y) && space[s * width + d];
                next[i * width + j] = current.rule[space[i * width + j]][wj + sj + ia + id + wa + wd + sa + sd];
            }
        }
    }
    bool undo() {
        if (undolog.empty()) {
            return 0;
        }
        redolog.push(current);
        if (auto rec = current.bound; (current = undolog.top()).bound && !rec) {
            reference = *current.bound;
        }
        undolog.pop();
        return 1;
    }
    bool redo() {
        if (redolog.empty()) {
            return 0;
        }
        undolog.push(current);
        if (auto rec = current.bound; (current = redolog.top()).bound && !rec) {
            reference = *current.bound;
        }
        redolog.pop();
        return 1;
    }
    auto get_generation() const {
        return current.generation;
    }
    auto get_ref_cell(uint16_t x, uint16_t y) const {
        return current.space[(x + reference.x) % height * width + (y + reference.y) % width];
    }
    uint16_t get_ref_location_x() const {
        return (height + location.x - reference.x) % height;
    }
    uint16_t get_ref_location_y() const {
        return (width + location.y - reference.y) % width;
    }
    auto get_width() const {
        return width;
    }
    auto get_height() const {
        return height;
    }
    bool save(std::string const &str) const {
        std::ofstream file(str);
        if (file.fail()) {
            return 0;
        }
        file << get_rule() << std::endl;
        file << height << '*' << width << ' ' << (current.bound ? '1' : '0') << std::endl;
        for (uint16_t i = 0; i < height; i++) {
            for (uint16_t j = 0; j < width; j++) {
                file << get_ref_cell(i, j);
            }
            file << std::endl;
        }
        return 1;
    }
    bool open(std::string const &str) {
        std::ifstream file(str);
        if (file.fail()) {
            return 0;
        }
        std::string rule;
        int h, w;
        char c, b;
        file >> rule >> h >> c >> w >> b;
        if (current.bound ? b == '0' : b != '0') {
            switch_mode();
        }
        set_rule(rule);
        reset_space(h, w);
        for (uint16_t i = 0; i < height; i++) {
            std::string line;
            file >> line;
            for (uint16_t j = 0; j < width; j++) {
                current.space[i * width + j] = line[j] == '1';
            }
        }
        return 1;
    }
};
template <bool rand, bool play>
void game(CellAuto const &ca, uint64_t interval) {
    uint16_t top = MAX((STD_HEIGHT - ca.get_height()) / 2, 0), left = MAX(STD_WIDTH - ca.get_width(), 0);
    uint32_t population = 0;
    WINDOW *info = newwin(3, 2 * ca.get_width() - 3, top, left);
    WINDOW *state = newwin(3, 6, top, 2 * ca.get_width() - 3 + left);
    WINDOW *space = newwin(ca.get_height() + 2, 2 * ca.get_width() + 3, top + 3, left);
    WINDOW *gen = newwin(1, 2 * ca.get_width() + 3, ca.get_height() + 5 + top, left);
    box(state, ACS_VLINE, ACS_HLINE);
    if (ca.get_mode()) {
        wattron(space, COLOR_PAIR(1));
        box(space, ACS_VLINE, ACS_HLINE);
        wattroff(space, COLOR_PAIR(1));
    } else {
        wattron(space, COLOR_PAIR(2));
        box(space, ACS_VLINE, ACS_HLINE);
        wattroff(space, COLOR_PAIR(2));
    }
    wattron(space, COLOR_PAIR(3));
    for (uint16_t i = 0; i < ca.get_height(); i++) {
        for (uint16_t j = 0; j < ca.get_width(); j++) {
            mvwaddch(space, i + 1, j * 2 + 2, ca.get_ref_cell(i, j) ? (population++, '*') : ' ');
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
        auto x = ca.get_ref_location_x(), y = ca.get_ref_location_y();
        mvwaddch(space, x + 1, y * 2 + 1, '>');
        mvwaddch(space, x + 1, y * 2 + 3, '<');
    }
    mvwprintw(info, 0, 0, "Rule = %s", ca.get_rule().c_str());
    mvwprintw(info, 1, 0, "Speed = %.2f", 1024.0 / interval);
    mvwprintw(info, 2, 0, "Generation = %lu", ca.get_generation());
    mvwprintw(gen, 0, 0, "%*s%04d", 2 * ca.get_width() - 1, "Population = ", population);
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
template <bool end>
void menu() {
    uint16_t top = MAX((LINES - 10) / 2, 0), left = MAX((COLS - 18) / 2, 0);
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
    if (end) {
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
int main(int argc, char *argv[]) {
    if (!isatty(fileno(stdin)) || !isatty(fileno(stdout))) {
        std::cerr << "error: unsupported stdin/stdout" << std::endl;
        return 1;
    }
    CellAuto ca(0, 0);
    int rec = 0, h, w;
    for (int i = 1; (rec & REC_ERR) == 0 && i < argc; i++) {
        if (argv[i][0] == '-') {
            if (argv[i][1] == 'b' && argv[i][2] == '\0') {
                if ((rec & (REC_OPN | REC_MOD)) == 0) {
                    ca.switch_mode();
                    rec |= REC_MOD;
                } else {
                    rec |= REC_ERR;
                }
            } else if (argv[i][1] == 'r' && argv[i][2] == '\0') {
                if ((rec & (REC_OPN | REC_RUL)) == 0 && i + 1 < argc) {
                    ca.set_rule(argv[++i]);
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
        } else if ((rec & (REC_MOD | REC_RUL | REC_SPA | REC_OPN)) == 0 && ca.open(argv[i])) {
            rec |= REC_OPN;
        } else {
            rec |= REC_ERR;
        }
    }
    if ((rec & REC_ERR) != 0) {
        std::cerr << "usage: " << argv[0] << " [-b] [-r RULE] [-n HEIGHT WIDTH] or " << argv[0] << " FILE" << std::endl;
        return 1;
    }
    auto win = initscr();
    if ((rec & REC_SPA) != 0) {
        ca.reset_space(h, w);
    } else if ((rec & REC_OPN) == 0) {
        ca.reset_space(STD_HEIGHT, STD_WIDTH);
    }
    noecho();
    curs_set(0);
    start_color();
    use_default_colors();
    init_pair(1, COLOR_RED, -1);
    init_pair(2, COLOR_GREEN, -1);
    init_pair(3, COLOR_YELLOW, -1);
    uint64_t interval = 1024, recd;
GAME_INIT:
    game<0, 0>(ca, interval);
GAME_REPT:
    switch (auto c = getch(); c) {
    case '-':
        interval = MIN(interval * 2, 4096);
        goto GAME_INIT;
    case '=':
        interval = MAX(interval / 2, 1);
        goto GAME_INIT;
    case 'b':
        ca.switch_mode();
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
    case 'h':
        while (ca.undo()) {}
        goto GAME_INIT;
    case 'e':
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
        ca.switch_cell();
        goto GAME_INIT;
    case 'w':
    case 's':
    case 'a':
    case 'd':
        ca.move_location(c);
        goto GAME_INIT;
    case 'W':
    case 'A':
    case 'S':
    case 'D':
        ca.move_reference(c + 32);
        goto GAME_INIT;
    case 'R':
        goto RAND_INIT;
    case ' ':
        recd = usec();
        nodelay(win, 1);
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
    game<1, 0>(ca, interval);
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
    game<0, 1>(ca, interval);
PLAY_REPT:
    switch (getch()) {
    case ' ':
        nodelay(win, 0);
        goto GAME_INIT;
    case KEY_RESIZE:
        clear();
        goto PLAY_INIT;
    default:
        if (auto nxtd = recd + interval * 1000; usec() < nxtd) {
            goto PLAY_REPT;
        } else {
            ca.step();
            recd = nxtd;
            goto PLAY_INIT;
        }
    }
MENU_INIT:
    menu<0>();
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
        bool success = ca.open(filename);
        std::cout << "=> " << (success ? "File opened successfully!" : "File open failed!") << std::endl;
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
        bool success = ca.save(filename);
        std::cout << "=> " << (success ? "File saved successfully!" : "File save failed!") << std::endl;
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
        std::string rule;
        std::cout << ">> Rule(B/S): ";
        while ((std::cin >> rule).fail()) {
            std::cin.clear();
        }
        ca.set_rule(rule);
        reset_prog_mode();
        goto GAME_INIT;
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
        ca.reset_space(h, w);
        reset_prog_mode();
        goto GAME_INIT;
    }
    case 'a':
        ca.reset_space(STD_HEIGHT, STD_WIDTH);
        goto GAME_INIT;
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
    menu<1>();
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
