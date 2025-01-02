#ifndef ENGINE_H
#define ENGINE_H

#include <bitset>
#include <string>
#include <sstream>
#include <vector>
#include <cstdint>
#include <unordered_set>

struct BoardState {
    std::bitset<24> blackPieces;
    std::bitset<24> whitePieces;
    std::int_fast8_t moveNumber = 0;
    bool isTurnWhite = true;    // if false, it is the black player's turn
    bool placingPhase = true;   // if false, it is the moving phase or later
    bool isLateGameWhite = false;
    bool isLateGameBlack = false;
    std::vector<std::unordered_set<int>> neighbors = {
        {1, 9},          // 0
        {0, 2, 4},       // 1
        {1, 14},         // 2
        {4, 10},         // 3
        {1, 3, 5, 7},    // 4
        {4, 13},         // 5
        {7, 11},         // 6
        {4, 6, 8},       // 7
        {7, 12},         // 8
        {0, 10, 21},     // 9
        {3, 9, 11, 18},  // 10
        {6, 10, 15},     // 11
        {8, 13, 17},     // 12
        {5, 12, 14, 20}, // 13
        {2, 13, 23},     // 14
        {11, 16},        // 15
        {15, 17, 19},    // 16
        {12, 16},        // 17
        {10, 19},        // 18
        {16, 18, 20, 22},// 19
        {13, 19},        // 20
        {9, 22},         // 21
        {19, 21, 23},    // 22
        {14, 22}         // 23
    };
    std::vector<std::unordered_set<int>> emptyNeighbors = {
        {1, 9},          // 0
        {0, 2, 4},       // 1
        {1, 14},         // 2
        {4, 10},         // 3
        {1, 3, 5, 7},    // 4
        {4, 13},         // 5
        {7, 11},         // 6
        {4, 6, 8},       // 7
        {7, 12},         // 8
        {0, 10, 21},     // 9
        {3, 9, 11, 18},  // 10
        {6, 10, 15},     // 11
        {8, 13, 17},     // 12
        {5, 12, 14, 20}, // 13
        {2, 13, 23},     // 14
        {11, 16},        // 15
        {15, 17, 19},    // 16
        {12, 16},        // 17
        {10, 19},        // 18
        {16, 18, 20, 22},// 19
        {13, 19},        // 20
        {9, 22},         // 21
        {19, 21, 23},    // 22
        {14, 22}         // 23
    };
};


std::string generateKey(const BoardState& state);

class History {
public:
    void saveState(const BoardState& state);
    const std::vector<BoardState>& getHistory() const;
    void deleteEntry(size_t index);
    void deleteLastEntry();
    void clearHistory();

private:
    std::vector<BoardState> history;
};

void checkPhase(BoardState& state);

void checkFunctionEmptyNeighbors(const BoardState state, int cell);

void inputAdd(BoardState& state, History& history);

void inputRemove(BoardState& state, History& history);

void inputMove(BoardState& state, History& history);

#endif // ENGINE_H