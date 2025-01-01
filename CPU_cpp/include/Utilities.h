#ifndef UTILITIES_H
#define UTILITIES_H

#include <iostream>
#include "Engine.h"

// Declaration and definition of the print function template
template <typename T>
void print(const T& message) {
    std::cout << message << std::endl;
}

// Overload the operator<< for BoardState
std::ostream& operator<<(std::ostream& os, const BoardState& boardState) {
    os << "Black Pieces: " << boardState.blackPieces << "\n";
    os << "White Pieces: " << boardState.whitePieces;
    return os;
}

#endif // UTILITIES_H