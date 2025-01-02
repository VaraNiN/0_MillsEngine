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
    std::bitset<24> emptySpaces = std::bitset<24>().set();
    std::int_fast8_t moveNumber = 0;
    bool isTurnWhite = true;    // if false, it is the black player's turn
    bool placingPhase = true;   // if false, it is the moving phase or later
    bool isLateGameWhite = false;
    bool isLateGameBlack = false;
    inline static const std::vector<std::unordered_set<int>> neighbors = {
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
    inline static const std::vector<std::bitset<24>> possibleMills = {
        std::bitset<24>("000000000000000000000111"), // Mill 1: {0, 1, 2}
        std::bitset<24>("000000000000000000111000"), // Mill 2: {3, 4, 5}
        std::bitset<24>("000000000000000111000000"), // Mill 3: {6, 7, 8}
        std::bitset<24>("000000000000111000000000"), // Mill 4: {9, 10, 11}
        std::bitset<24>("000000000111000000000000"), // Mill 5: {12, 13, 14}
        std::bitset<24>("000000111000000000000000"), // Mill 6: {15, 16, 17}
        std::bitset<24>("000111000000000000000000"), // Mill 7: {18, 19, 20}
        std::bitset<24>("111000000000000000000000"), // Mill 8: {21, 22, 23}
        std::bitset<24>("001000000000001000000001"), // Mill 9: {0, 9, 21}
        std::bitset<24>("000001000000010000001000"), // Mill 10: {3, 10, 18}
        std::bitset<24>("000000001000100001000000"), // Mill 11: {6, 11, 15}
        std::bitset<24>("000000000000000010010010"), // Mill 12: {1, 4, 7}
        std::bitset<24>("010010010000000000000000"), // Mill 13: {16, 19, 22}
        std::bitset<24>("000000100001000100000000"), // Mill 14: {8, 12, 17}
        std::bitset<24>("000100000010000000100000"), // Mill 15: {5, 13, 20}
        std::bitset<24>("100000000100000000000100"), // Mill 16: {2, 14, 23}
    };
    inline static const std::vector<std::bitset<24>> possibleDoubleMills = {
        std::bitset<24>("000000000000000000111101"), // Mill 1 + Mill 2
        std::bitset<24>("000000000000000000101111"), // Mill 1 + Mill 2
        std::bitset<24>("000000000000000111101000"), // Mill 2 + Mill 3
        std::bitset<24>("000000000000000101111000"), // Mill 2 + Mill 3
        std::bitset<24>("000111101000000000000000"), // Mill 6 + Mill 7
        std::bitset<24>("000101111000000000000000"), // Mill 6 + Mill 7
        std::bitset<24>("111101000000000000000000"), // Mill 7 + Mill 8
        std::bitset<24>("101111000000000000000000"), // Mill 7 + Mill 8
        std::bitset<24>("001001000000010000001001"), // Mill 9 + Mill 10
        std::bitset<24>("001001000000001000001001"), // Mill 9 + Mill 10
        std::bitset<24>("000001001000100001001000"), // Mill 10 + Mill 11
        std::bitset<24>("000001001000010001001000"), // Mill 10 + Mill 11
        std::bitset<24>("000100100010000100100000"), // Mill 14 + Mill 15
        std::bitset<24>("000100100001000100100000"), // Mill 14 + Mill 15
        std::bitset<24>("100100000100000000100100"), // Mill 15 + Mill 16
        std::bitset<24>("100100000010000000100100"), // Mill 15 + Mill 16
    };
    inline static const std::vector<std::bitset<24>> doubleMillBlockers = {
        std::bitset<24>("000000000000000000000010"), // Mill 1 + Mill 2
        std::bitset<24>("000000000000000000010000"), // Mill 1 + Mill 2
        std::bitset<24>("000000000000000000010000"), // Mill 2 + Mill 3
        std::bitset<24>("000000000000000010000000"), // Mill 2 + Mill 3
        std::bitset<24>("000000010000000000000000"), // Mill 6 + Mill 7
        std::bitset<24>("000010000000000000000000"), // Mill 6 + Mill 7
        std::bitset<24>("000010000000000000000000"), // Mill 7 + Mill 8
        std::bitset<24>("010000000000000000000000"), // Mill 7 + Mill 8
        std::bitset<24>("000000000000001000000000"), // Mill 9 + Mill 10
        std::bitset<24>("000000000000010000000000"), // Mill 9 + Mill 10
        std::bitset<24>("000000000000010000000000"), // Mill 10 + Mill 11
        std::bitset<24>("000000000000100000000000"), // Mill 10 + Mill 11
        std::bitset<24>("000000000001000000000000"), // Mill 14 + Mill 15
        std::bitset<24>("000000000010000000000000"), // Mill 14 + Mill 15
        std::bitset<24>("000000000010000000000000"), // Mill 15 + Mill 16
        std::bitset<24>("000000000100000000000000"), // Mill 15 + Mill 16
    };
};

std::bitset<50> generateKey(const BoardState& state);

std::bitset<50> generateKey2(const BoardState& state);

std::bitset<50> generateKey3(const BoardState state);

std::bitset<50> generateKey4(const BoardState state);

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

void checkValidity(const BoardState& state);

void checkPhase(BoardState& state);

#endif // ENGINE_H