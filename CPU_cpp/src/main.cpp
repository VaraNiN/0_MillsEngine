#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"
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

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    for (int i = 0; i < 16; i++) {
        state.whitePieces = state.possibleDoubleMills[i];
        state.blackPieces = state.doubleMillBlockers[i];
        show_position(state);
    }


    // Timing bitwise AND operation
    int its = 1e6;
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < its; i++){
        for (std::bitset<24> possibleMill : state.possibleMills) {
            bool isMill = (state.whitePieces & possibleMill).count() == 3;
            //print(isMill);
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;
    std::cout << "Average check if a mill occurred: " << 1e9 * duration.count()/its << " ns\n";


    // Timing bitwise AND operation
    start = std::chrono::high_resolution_clock::now();
    for (int j = 0; j < 16; j++){
        for (int i = 0; i < its; i++){
            //std::bitset<24> result = generateRandomBitset() & state.doubleMillBlockers[j];
            std::bitset<24> result = state.whitePieces & state.doubleMillBlockers[j];
            bool isNonZero = result.any();
        }
    }
    end = std::chrono::high_resolution_clock::now();
    duration = end - start;
    std::cout << "Average bitwise AND operation took: " << 1e9 * duration.count()/(16*its) << " ns\n";

    // Timing specific entry lookup
    start = std::chrono::high_resolution_clock::now();
    for (int j = 0; j < 16; j++){
        for (int i = 0; i < its; i++){
            //std::bitset<24> bitset = generateRandomBitset();
            //bool specificEntry = bitset[5];
            bool specificEntry = state.whitePieces[j];
        }
    }
    end = std::chrono::high_resolution_clock::now();
    duration = end - start;
    std::cout << "Specific entry lookup took: " << 1e9 * duration.count()/(16*its) << " ns\n";

    return 0;
}