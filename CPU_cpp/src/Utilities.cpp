#include "Engine.h"
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
    if (!dummyState.whitePieces.any() & !dummyState.blackPieces.any()) {
        dummyState.whitePieces = generateRandomBitset();
        dummyState.blackPieces = generateRandomBitset();
    }

    float eval;

    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < its; i++){
        if (i % pos_every == 0) {
            end = std::chrono::high_resolution_clock::now();
            duration += end - start;
            if (!dummyState.whitePieces.any() & !dummyState.blackPieces.any()) {
                dummyState.whitePieces = generateRandomBitset();
                dummyState.blackPieces = generateRandomBitset();
            }
            start = std::chrono::high_resolution_clock::now();
        }
        // enter Function here
        eval = evaluate(dummyState);
    }
    end = std::chrono::high_resolution_clock::now();
    duration += end - start;
    std::cout << "Operations took: " << duration.count() << " seconds\n";
    std::cout << "Average: " << 1e6 * duration.count() / its << " µs\n\n";


}