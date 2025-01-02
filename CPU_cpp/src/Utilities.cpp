#include "Engine.h"
#include "GUI.h"
#include <iostream>
#include <random>
#include <chrono>

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

std::bitset<24> generateRandomBitset() {
    std::random_device rd;  // Seed for the random number generator
    std::mt19937 gen(rd()); // Mersenne Twister engine
    std::uniform_int_distribution<> dis(0, 1); // Distribution to generate 0 or 1

    std::bitset<24> randomBitset;
    for (size_t i = 0; i < randomBitset.size(); ++i) {
        randomBitset[i] = dis(gen);
    }
    return randomBitset;
}

void timeStuff(const BoardState& state, int its, int pos_every) {
    auto start = std::chrono::high_resolution_clock::now();
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;
    BoardState dummyState = state;
    if (!state.whitePieces.any() & !state.blackPieces.any()) {
        auto dummy1 = generateRandomBitset();
        auto dummy2 = generateRandomBitset();
        dummyState.whitePieces = dummy1 & dummy2;
        dummyState.blackPieces = ~(dummy1 | dummy2);
    }

    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < its; i++){
        if (i % pos_every == 0) {
            end = std::chrono::high_resolution_clock::now();
            duration += end - start;
            if (!state.whitePieces.any() & !state.blackPieces.any()) {
                auto dummy1 = generateRandomBitset();
                auto dummy2 = generateRandomBitset();
                dummyState.whitePieces = dummy1 & dummy2;
                dummyState.blackPieces = ~(dummy1 | dummy2);
                dummyState.isPlacingPhase ^= true;
            }
            start = std::chrono::high_resolution_clock::now();
        }
        // enter Function here
        auto dummy = getChildren(dummyState);
    }
    end = std::chrono::high_resolution_clock::now();
    duration += end - start;
    std::cout << "Operations took: " << duration.count() << " seconds\n";
    std::cout << "Average: " << 1e6 * duration.count() / its << " µs\n\n";


}