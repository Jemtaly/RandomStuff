#include <math.h>
#include <stdlib.h>
#include <sys/time.h>
#include <unistd.h>
#include <fstream>
#include <iostream>
#include <stack>
#include "curses.h"
#define COLOR_LIVES 6
#define TRIPLET 2.0943951023931953
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
#define REC_SPC 4
#define REC_FLS 128
uint64_t usec() {
	timeval tv;
	gettimeofday(&tv, NULL);
	return (uint64_t)tv.tv_sec * 1000000 + tv.tv_usec;
}
auto init_rainbow(int const &c, double const &theta) {
	return init_color(c, floor(500 + 500 * cos(theta)), floor(500 + 500 * cos(theta - TRIPLET)), floor(500 + 500 * cos(theta + TRIPLET)));
}
bool **new_space(uint16_t const &h, uint16_t const &w) {
	bool **space_new = new bool *[h];
	for (uint16_t i = 0; i < h; i++) {
		space_new[i] = new bool[w]();
	}
	return space_new;
}
bool **clone_space(bool **const &space_src, uint16_t const &h, uint16_t const &w) {
	bool **space_dst = new bool *[h];
	for (uint16_t i = 0; i < h; i++) {
		space_dst[i] = new bool[w];
		for (uint16_t j = 0; j < w; j++) {
			space_dst[i][j] = space_src[i][j];
		}
	}
	return space_dst;
}
void delete_space(bool **const &space_dlt, uint16_t const &h, uint16_t const &w) {
	for (uint16_t i = 0; i < h; i++) {
		delete[] space_dlt[i];
	}
	delete[] space_dlt;
}
class CellAuto {
	uint16_t height, width;
	struct XY {
		uint16_t x, y;
	} location, reference;
	struct GenerationInfo {
		bool **space;
		bool rule[2][9];
		XY *bound;
		size_t generation;
	} current;
	std::stack<GenerationInfo> undolog, redolog;
	void clear_undolog() {
		for (auto bound = current.bound; !undolog.empty(); undolog.pop()) {
			delete_space(undolog.top().space, height, width);
			if (auto rec = bound; (bound = undolog.top().bound) && !rec) {
				delete bound;
			}
		}
	}
	void clear_redolog() {
		for (auto bound = current.bound; !redolog.empty(); redolog.pop()) {
			delete_space(redolog.top().space, height, width);
			if (auto rec = bound; (bound = redolog.top().bound) && !rec) {
				delete bound;
			}
		}
	}
	void apply_generation(bool **const &space) {
		clear_redolog();
		undolog.push(current);
		current.space = space;
	}
	void init_generation() {
		clear_undolog();
		clear_redolog();
		current.generation = 0;
	}
public:
	CellAuto(CellAuto const &) = delete;
	CellAuto &operator=(CellAuto const &) = delete;
	CellAuto(int const &h, int const &w):
		height(h < MIN_HEIGHT ? MIN_HEIGHT : h > MAX_HEIGHT ? MAX_HEIGHT : h),
		width(w < MIN_WIDTH ? MIN_WIDTH : w > MAX_WIDTH ? MAX_WIDTH : w),
		location{0, 0},
		reference{0, 0},
		current{new_space(height, width), {{0, 0, 0, 1, 0, 0, 0, 0, 0}, {0, 0, 1, 1, 0, 0, 0, 0, 0}}, nullptr, 0} {}
	~CellAuto() {
		clear_undolog();
		clear_redolog();
		delete_space(current.space, height, width);
		if (current.bound) {
			delete current.bound;
		}
	}
	void move_location(char const &dir) {
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
	void move_reference(char const &dir) {
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
	void reset_space(int const &h, int const &w) {
		init_generation();
		delete_space(current.space, height, width);
		height = h < MIN_HEIGHT ? MIN_HEIGHT : h > MAX_HEIGHT ? MAX_HEIGHT : h;
		width = w < MIN_WIDTH ? MIN_WIDTH : w > MAX_WIDTH ? MAX_WIDTH : w;
		current.space = new_space(height, width);
		if (current.bound) {
			current.bound->x = current.bound->y = 0;
		}
		reference.x = reference.y = location.x = location.y = 0;
	}
	void random_space(uint8_t const &d) {
		init_generation();
		for (uint16_t i = 0; i < height; i++) {
			for (uint16_t j = 0; j < width; j++) {
				current.space[i][j] = rand() % 8 < d;
			}
		}
	}
	void set_rule(std::string const &rule) {
		bool new_rule[2][9] = {};
		for (bool i = 0; auto r : rule) {
			switch (r) {
			case '/':
				i ^= 1;
				break;
			case 'b':
			case 'B':
				i = 0;
				break;
			case 's':
			case 'S':
				i = 1;
				break;
			default:
				if (r >= '0' && r <= '8') {
					new_rule[i][r - '0'] = 1;
				}
			}
		}
		bool changed = 0;
		for (int i = 0; i < 9; i++) {
			changed |= current.rule[0][i] != new_rule[0][i] || current.rule[1][i] != new_rule[1][i];
		}
		if (changed) {
			apply_generation(clone_space(current.space, height, width));
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
		apply_generation(clone_space(current.space, height, width));
		current.bound = current.bound ? nullptr : new XY(reference);
	}
	bool get_mode() const {
		return current.bound;
	}
	void switch_cell() {
		apply_generation(clone_space(current.space, height, width));
		current.space[location.x][location.y] ^= 1;
	}
	void set_cell(bool const &n) {
		if (current.space[location.x][location.y] != n) {
			switch_cell();
		}
	}
	void step() {
		bool **space_step = new_space(height, width);
		for (uint16_t i = 0; i < height; i++) {
			for (uint16_t j = 0; j < width; j++) {
				uint16_t reference_x = reference.x == 0 ? height - 1 : reference.x - 1, reference_y = reference.y == 0 ? width - 1 : reference.y - 1;
				uint16_t w = i == 0 ? height - 1 : i - 1, s = i == height - 1 ? 0 : i + 1, a = j == 0 ? width - 1 : j - 1, d = j == width - 1 ? 0 : j + 1;
				bool wj = (!current.bound || i != reference.x) && current.space[w][j];
				bool sj = (!current.bound || i != reference_x) && current.space[s][j];
				bool ia = (!current.bound || j != reference.y) && current.space[i][a];
				bool id = (!current.bound || j != reference_y) && current.space[i][d];
				bool wa = (!current.bound || i != reference.x && j != reference.y) && current.space[w][a];
				bool wd = (!current.bound || i != reference.x && j != reference_y) && current.space[w][d];
				bool sa = (!current.bound || i != reference_x && j != reference.y) && current.space[s][a];
				bool sd = (!current.bound || i != reference_x && j != reference_y) && current.space[s][d];
				space_step[i][j] = current.rule[current.space[i][j]][wj + sj + ia + id + wa + wd + sa + sd];
			}
		}
		apply_generation(space_step);
		current.generation++;
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
	auto const &get_generation() const {
		return current.generation;
	}
	auto const &get_ref_cell(uint16_t const &x, uint16_t const &y) const {
		return current.space[(x + reference.x) % height][(y + reference.y) % width];
	}
	uint16_t get_ref_location_x() const {
		return (height + location.x - reference.x) % height;
	}
	uint16_t get_ref_location_y() const {
		return (width + location.y - reference.y) % width;
	}
	auto const &get_width() const {
		return width;
	}
	auto const &get_height() const {
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
		if (b != (current.bound ? '1' : '0')) {
			switch_mode();
		}
		set_rule(rule);
		reset_space(h, w);
		for (uint16_t i = 0; i < height; i++) {
			std::string line;
			file >> line;
			for (uint16_t j = 0; j < width; j++) {
				current.space[i][j] = line[j] == '1';
			}
		}
		return 1;
	}
};
void show(CellAuto const &ca, uint64_t const &interval, int const &block) {
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
	if ((block & 2) == 0) {
		auto x = ca.get_ref_location_x(), y = ca.get_ref_location_y();
		mvwaddch(space, x + 1, y * 2 + 1, '>');
		mvwaddch(space, x + 1, y * 2 + 3, '<');
		wattron(state, COLOR_PAIR(1));
		mvwaddstr(state, 1, 2, "||");
		wattroff(state, COLOR_PAIR(1));
	} else {
		wattron(state, COLOR_PAIR(2));
		mvwaddstr(state, 1, 2, "|>");
		wattroff(state, COLOR_PAIR(2));
	}
	mvwprintw(info, 0, 0, "Rule = %s", ca.get_rule().c_str());
	mvwprintw(info, 1, 0, "Speed = %.2f", 1024.0 / interval);
	mvwprintw(info, 2, 0, "Generation = %d", ca.get_generation());
	mvwprintw(gen, 0, 0, "%*s%04d", 2 * ca.get_width() - 1, "Population = ", population);
	if ((block & 1) != 0) {
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
void show_menu(bool const &end) {
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
	uint64_t interval = 1024;
	CellAuto ca(0, 0);
	int rec = 0;
	for (int i = 1; (rec & REC_FLS) == 0 && i < argc; i++) {
		if (argv[i][0] == '-') {
			if (argv[i][1] == 'b' && argv[i][2] == '\0') {
				if ((rec & REC_MOD) == 0) {
					ca.switch_mode();
					rec |= REC_MOD;
				} else {
					rec |= REC_FLS;
				}
			} else if (argv[i][1] == 'r' && argv[i][2] == '\0') {
				if ((rec & REC_RUL) == 0 && i + 1 < argc) {
					ca.set_rule(argv[++i]);
					rec |= REC_RUL;
				} else {
					rec |= REC_FLS;
				}
			} else if (argv[i][1] == 'n' && argv[i][2] == '\0') {
				if ((rec & REC_SPC) == 0 && i + 2 < argc) {
					int h = atoi(argv[++i]);
					int w = atoi(argv[++i]);
					ca.reset_space(h, w);
					rec |= REC_SPC;
				} else {
					rec |= REC_FLS;
				}
			} else {
				rec |= REC_FLS;
			}
		} else if (rec == 0 && ca.open(argv[i])) {
			rec |= REC_MOD | REC_RUL | REC_SPC;
		} else {
			rec |= REC_FLS;
		}
	}
	if ((rec & REC_FLS) != 0) {
		std::cerr << "usage: " << argv[0] << " [-b] [-r RULE] [-n H W] or " << argv[0] << " FILENAME" << std::endl;
		return 1;
	}
	auto win = initscr();
	if ((rec & REC_SPC) == 0) {
		ca.reset_space(STD_HEIGHT, STD_WIDTH);
	}
	noecho();
	curs_set(0);
	start_color();
	use_default_colors();
	init_rainbow(COLOR_LIVES, 0);
	init_pair(1, COLOR_RED, -1);
	init_pair(2, COLOR_GREEN, -1);
	init_pair(3, COLOR_LIVES, -1);
GAME_SHOW:
	show(ca, interval, 0);
GAME_READ:
	switch (auto c = getch(); c) {
	case '-':
		interval = MIN(interval * 2, 4096);
		goto GAME_SHOW;
	case '=':
		interval = MAX(interval / 2, 1);
		goto GAME_SHOW;
	case 'b':
		ca.switch_mode();
		goto GAME_SHOW;
	case '`':
		ca.step();
		goto GAME_SHOW;
	case ',':
		ca.undo();
		goto GAME_SHOW;
	case '.':
		ca.redo();
		goto GAME_SHOW;
	case 'h':
		while (ca.undo()) {}
		goto GAME_SHOW;
	case 'e':
		while (ca.redo()) {}
		goto GAME_SHOW;
	case 'c':
		ca.random_space(0);
		goto GAME_SHOW;
	case 'r':
		ca.random_space(2);
		goto GAME_SHOW;
	case '0':
		ca.set_cell(0);
		goto GAME_SHOW;
	case '1':
		ca.set_cell(1);
		goto GAME_SHOW;
	case '8':
		ca.switch_cell();
		goto GAME_SHOW;
	case 'w':
	case 's':
	case 'a':
	case 'd':
		ca.move_location(c);
		goto GAME_SHOW;
	case 'W':
	case 'A':
	case 'S':
	case 'D':
		ca.move_reference(c + 32);
		goto GAME_SHOW;
	case 'R':
	RAND_SHOW:
		show(ca, interval, 1);
	RAND_READ:
		if (auto r = getch(); r >= '0' && r <= '9') {
			ca.random_space(r - '0');
			goto GAME_SHOW;
		} else if (r == KEY_RESIZE) {
			clear();
			goto RAND_SHOW;
		} else {
			goto RAND_READ;
		}
	case ' ':
		nodelay(win, 1);
		for (uint64_t start = usec();;) {
			uint64_t end = usec() + interval * 1000, now;
		PLAY_SHOW:
			show(ca, interval, 2);
			do {
				switch (getch()) {
				case ' ':
					nodelay(win, 0);
					init_rainbow(COLOR_LIVES, 0);
					goto GAME_SHOW;
				case KEY_RESIZE:
					clear();
					goto PLAY_SHOW;
				}
				now = usec();
				init_rainbow(COLOR_LIVES, (double)(now - start) / 1e6);
				refresh();
			} while (now < end);
			ca.step();
		}
	case 'm':
		clear();
	MENU_SHOW:
		show_menu(0);
	MENU_READ:
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
				goto GAME_SHOW;
			} else {
				goto MENU_SHOW;
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
				goto GAME_SHOW;
			} else {
				goto MENU_SHOW;
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
			goto GAME_SHOW;
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
			goto GAME_SHOW;
		}
		case 'a':
			ca.reset_space(STD_HEIGHT, STD_WIDTH);
		case 'c':
			goto GAME_SHOW;
		case 'q':
		QUIT_SHOW:
			show_menu(1);
		QUIT_READ:
			switch (getch()) {
			case 'y':
				endwin();
				return 0;
			case 'n':
				goto MENU_SHOW;
			case KEY_RESIZE:
				clear();
				goto QUIT_SHOW;
			default:
				goto QUIT_READ;
			}
		case KEY_RESIZE:
			clear();
			goto MENU_SHOW;
		default:
			goto MENU_READ;
		}
	case KEY_RESIZE:
		clear();
		goto GAME_SHOW;
	default:
		goto GAME_READ;
	}
}
