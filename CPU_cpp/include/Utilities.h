#ifndef UTILITIES_H
#define UTILITIES_H

#include <iostream>
#include "Engine.h"

std::ostream& operator<<(std::ostream& os, const BoardState& boardState) {
    os << "White Pieces: " << boardState.whitePieces << "\n";
    os << "Black Pieces: " << boardState.blackPieces << "\n";
    os << "Empty Spaces: " << boardState.emptySpaces << "\n";
    os << "Move Number: " << static_cast<int>(boardState.moveNumber) << "\n";
    os << "Is it white's turn: " << (boardState.isTurnWhite ? "Yes" : "No") << "\n";
    os << "Placing Phase: " << (boardState.isPlacingPhase ? "Yes" : "No") << "\n";
    os << "Flying phase for White: " << (boardState.isFlyingPhaseWhite ? "Yes" : "No") << "\n";
    os << "Flying phase for Black: " << (boardState.isFlyingPhaseBlack ? "Yes" : "No") << "\n";
    return os;
}

// Other functions

void checkFunctionEmptyNeighbors(const BoardState state, int cell);

std::bitset<24> generateRandomBitset();

void timeStuff(const BoardState& state, int its = 1e6, int pos_every = 1e2);

#endif // UTILITIES_H