#ifndef ENGINE_H
#define ENGINE_H

#include <bitset>
#include <string>
#include <sstream>
#include <vector>
#include <cstdint>

struct BoardState {
    std::bitset<24> blackPieces;
    std::bitset<24> whitePieces;
    std::int_fast8_t moveNumber = 0;
    bool isTurnWhite = true;    // if false, it is the black player's turn
    bool placingPhase = true;   // if false, it is the moving phase or later
    bool isLateGameWhite = false;
    bool isLateGameBlack = false;
};

std::string generateKey(const BoardState& state);

class History {
public:
    void saveState(const BoardState& state);
    const std::vector<BoardState>& getHistory() const;

private:
    std::vector<BoardState> history;
};

#endif // ENGINE_H