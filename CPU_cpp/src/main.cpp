#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"
#include "UserInput.h"
#include <iostream>
#include <bitset>
#include <chrono>

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    if (false) {
        int its = 1000;
        int every_pos = 20;

        timeStuff(state, its, every_pos);

        return 0;
    }


    auto start = std::chrono::high_resolution_clock::now();
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    while (true) {
        inputAdd(state, history);
        start = std::chrono::high_resolution_clock::now();
        callCount = 0;
        leaveCount = 0;
        auto [eval, newState] = minimax(state, 5, -10000, 10000, false);
        end = std::chrono::high_resolution_clock::now();
        duration = end - start;
        std::cout << "There were " << callCount << " minimax calls (" << leaveCount << " leafs) taking " << duration.count() << " seconds \n";
        std::cout << "Average call length: " << 1e6 * duration.count() / callCount << " µs\n\n";
        state = newState;
        //checkFunctionEmptyNeighbors(state);
        history.saveState(state);
    }



    //state.whitePieces = generateRandomBitset();
    //state.blackPieces = generateRandomBitset();
    //timeStuff(state);

    return 0;
}