#ifndef ENGINE_H
#define ENGINE_H

#include <bitset>

struct BoardState {
    std::bitset<24> blackPieces;
    std::bitset<24> whitePieces;
};

#endif // ENGINE_H