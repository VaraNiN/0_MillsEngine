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

void timeStuff(BoardState state, int its) {
    std::bitset<50> key;



    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < its; i++){
        // enter Function here
        key = generateKey(state);
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;
    std::cout << "Operations took: " << duration.count() << " seconds\n";
    std::cout << "Average: " << 1e6 * duration.count() / its << " µs\n\n";



    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < its; i++){
        // enter Function here
        key = generateKey(state);
    }
    end = std::chrono::high_resolution_clock::now();
    duration = end - start;
    std::cout << "Operations took: " << duration.count() << " seconds\n";
    std::cout << "Average: " << 1e6 * duration.count() / its << " µs\n\n";
}