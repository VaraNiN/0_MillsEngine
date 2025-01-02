#include "Engine.h"
#include "GUI.h"
#include <bitset>
#include <string>
#include <sstream>
#include <vector>
#include <cstdint>
#include <iostream>
#include <cstdlib>


std::bitset<50> generateKey(const BoardState& state) {
        std::bitset<50> key;
        key[0] = state.isTurnWhite;
        key[1] = state.placingPhase;
        std::bitset<50> piecesExtended(state.whitePieces.to_ulong());
        key |= (piecesExtended << 2);
        piecesExtended = std::bitset<50>(state.blackPieces.to_ulong());
        key |= (piecesExtended << 26);
        return key;
}

void History::saveState(const BoardState& state) {
    history.push_back(state);
}

const std::vector<BoardState>& History::getHistory() const {
    return history;
}

void History::deleteEntry(size_t index) {
    if (index < history.size()) {
        history.erase(history.begin() + index);
    } else {
        std::cout << "Index out of range!" << std::endl;
    }
}

void History::deleteLastEntry() {
    if (!history.empty()) {
        history.pop_back();
    } else {
        std::cout << "History is empty!" << std::endl;
    }
}

void History::clearHistory() {
    history.clear();
}

// Checks if position is valid
void checkValidity(const BoardState& state){
    if ((state.whitePieces & state.blackPieces).any()) {
        throw std::runtime_error("Error: Two pieces occupy the same position!");
    } else if ((state.whitePieces & state.emptySpaces).any()) {
        throw std::runtime_error("Error: Empty spaces are set wrong!");
    } else if ((state.blackPieces & state.emptySpaces).any()) {
        throw std::runtime_error("Error: Empty spaces are set wrong!");
    } else {
        std::cout << "Boardstate is valid!" << std::endl;
    }
}

// Checks which game phase it is
void checkPhase(BoardState& state) {
    state.placingPhase = (state.moveNumber < 18);

    if (!state.placingPhase) {
        state.isLateGameWhite = (state.whitePieces.count() == 3);
        state.isLateGameBlack = (state.blackPieces.count() == 3);
    }
}

std::vector<BoardState> getChildren(const BoardState& state) {
    std::vector<BoardState> children;
    BoardState dummyState = state;

    if (state.placingPhase) {
        for (int i = 0; i < 24; i++) {
            if (state.emptySpaces[i]) {
                if (state.isTurnWhite) {
                    dummyState.whitePieces.set(i);
                    children.push_back(dummyState);
                    dummyState = state;
                } else {
                    dummyState.blackPieces.set(i);
                    children.push_back(dummyState);
                    dummyState = state;
                }
            }
        }
    }

    return children;
}