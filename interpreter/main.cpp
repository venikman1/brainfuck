#include <stdio.h>
#include <string>
#include <vector>
#include <fstream>
#include <unordered_map>

bool is_command(char c) {
    return (
        c == '+' || c == '-' || c == '<' || c == '>' ||
        c == '.' || c == ',' || c == '[' || c == ']'
    );
}

void clean_code(std::string& code) {
    int w = 0;
    for (int r = 0; r <= code.size(); ++r) {
        if (is_command(code[r])) {
            code[w++] = code[r];
        }
    }
    code.resize(w);
}

std::unordered_map<int, int> get_bracket_pairs(const std::string& code) {
    std::unordered_map<int, int> pairs;
    std::vector<int> opened_brackets;
    for (int i = 0; i < code.size(); ++i) {
        if (code[i] == '[') {
            opened_brackets.push_back(i);
        }
        if (code[i] == ']') {
            int left = opened_brackets.back();
            pairs[left] = i;
            pairs[i] = left;
            opened_brackets.pop_back();
        }
    }
    return pairs;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("Usage: %s <code filename>\n", argv[0]);
    }
    std::ifstream code_file(argv[1]);
    std::string code;
    code_file >> code;
    code_file.close();
    clean_code(code);

    std::unordered_map<int, int> bracket_pairs = get_bracket_pairs(code);
    std::vector<char> memory(1000);
    std::vector<int> cycle_stack();
    int memory_pointer = 0;
    int code_pointer = 0;
    while (code_pointer < code.size()) {
        switch (code[code_pointer]) {
            case '+':
                ++memory[memory_pointer];
                ++code_pointer;
                break;
            case '-':
                --memory[memory_pointer];
                ++code_pointer;
                break;
            case '>':
                ++memory_pointer;
                ++code_pointer;
                break;
            case '<':
                --memory_pointer;
                ++code_pointer;
                break;
            case '[':
                if (memory[memory_pointer]) {
                    ++code_pointer;
                }
                else {
                    code_pointer = bracket_pairs.at(code_pointer) + 1;
                }
                break;
            case ']':
                code_pointer = bracket_pairs.at(code_pointer);
                break;
            case '.':
                putchar(memory[memory_pointer]);
                ++code_pointer;
                break;
            case ',':
                memory[memory_pointer] = getchar();
                ++code_pointer;
                break;
        }
    }
}