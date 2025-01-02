#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"
#include "UserInput.h"
#include <iostream>
#include <bitset>
#include <random>
#include <chrono>

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

void timeStuff(BoardState state, int its = 1e6) {
    std::bitset<50> key;

    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < its; i++){
        key = generateKey(state);
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;
    std::cout << "Operations took: " << duration.count() << " seconds\n";
    std::cout << "Average: " << 1e6 * duration.count() / its << " µs\n\n";

    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < its; i++){
        key = generateKey2(state);
    }
    end = std::chrono::high_resolution_clock::now();
    duration = end - start;
    std::cout << "Operations took: " << duration.count() << " seconds\n";
    std::cout << "Average: " << 1e6 * duration.count() / its << " µs\n\n";

    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < its; i++){
        key = generateKey3(state);
    }
    end = std::chrono::high_resolution_clock::now();
    duration = end - start;
    std::cout << "Operations took: " << duration.count() << " seconds\n";
    std::cout << "Average: " << 1e6 * duration.count() / its << " µs\n\n";

    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < its; i++){
        key = generateKey4(state);
    }
    end = std::chrono::high_resolution_clock::now();
    duration = end - start;
    std::cout << "Operations took: " << duration.count() << " seconds\n";
    std::cout << "Average: " << 1e6 * duration.count() / its << " µs\n\n";
}

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    state.whitePieces = generateRandomBitset();
    state.blackPieces = generateRandomBitset();

    timeStuff(state);


    return 0;
}