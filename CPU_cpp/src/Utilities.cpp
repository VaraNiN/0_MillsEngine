#include "Engine.h"
#include <iostream>

// Debugging function for the empty neighbors map
void checkFunctionEmptyNeighbors(const BoardState state, int cell) {
    for (int neighbor : state.neighbors[cell]) {
        std::cout << "\n\nEmpty neighbors of cell " << neighbor << " :\n";
        for (int neigborsneighbor : state.emptyNeighbors[neighbor]){
            std::cout << neigborsneighbor << " ";
        }
    }
    std::cout << std::endl;
}