#ifndef UTILITIES_H
#define UTILITIES_H

#include <iostream>
#include "Engine.h"

std::ostream& operator<<(std::ostream& os, const BoardState& boardState) {
    os << "Black Pieces: " << boardState.blackPieces << "\n";
    os << "White Pieces: " << boardState.whitePieces << "\n";
    os << "Move Number: " << static_cast<int>(boardState.moveNumber) << "\n";
    os << "Is Turn White: " << (boardState.isTurnWhite ? "Yes" : "No") << "\n";
    os << "Placing Phase: " << (boardState.placingPhase ? "Yes" : "No") << "\n";
    os << "Is Late Game White: " << (boardState.isLateGameWhite ? "Yes" : "No") << "\n";
    os << "Is Late Game Black: " << (boardState.isLateGameBlack ? "Yes" : "No") << "\n";
    return os;
}

template <typename T>
void print(const T& message) {
    std::cout << message << std::endl;
}

// Other functions

void checkFunctionEmptyNeighbors(const BoardState state, int cell);

#endif // UTILITIES_H