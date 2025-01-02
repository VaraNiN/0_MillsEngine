#include "Engine.h"
#include "GUI.h"
#include <bitset>
#include <string>
#include <sstream>
#include <vector>
#include <cstdint>
#include <iostream>
#include <cstdlib>


std::string generateKey(const BoardState& state) {
    std::ostringstream keyStream;
    keyStream << state.blackPieces.to_string()
              << state.whitePieces.to_string()
              << state.isTurnWhite
              << state.placingPhase
              << state.isLateGameWhite
              << state.isLateGameBlack;
    return keyStream.str();
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

// Checks which game phase it is and if position is valid
void checkPhase(BoardState& state) {
    if ((state.whitePieces & state.blackPieces).any()) {
        throw std::runtime_error("Error: Two pieces occupy the same position!");
    }

    state.placingPhase = (state.moveNumber < 18);

    if (!state.placingPhase) {
        state.isLateGameWhite = (state.whitePieces.count() == 3);
        state.isLateGameBlack = (state.blackPieces.count() == 3);
    }
}

// Adds a single piece to the board and appends that state to history
void inputAdd(BoardState& state, History& history) {
    std::vector<int> position = runMillsBoard(state, 1);
    
    if (position[0] == -1) {
        std::vector<BoardState> hist = history.getHistory();
        try {
            state = hist.at(hist.size() - 2);
            history.deleteLastEntry();
        } catch (const std::out_of_range& e) {
            std::cout << "Not enough history to go back half a step!" << std::endl;
        }
    } else if (position[0] == -2) {
        std::vector<BoardState> hist = history.getHistory();
        try {
            state = hist.at(hist.size() - 3);
            history.deleteLastEntry();
            history.deleteLastEntry();
        } catch (const std::out_of_range& e) {
            std::cout << "Not enough history to go back a full step!" << std::endl;
        }
    } else if (position[0] == -3) {
        exit(0);
    } else if (state.whitePieces[position[0]] != 0 || state.blackPieces[position[0]] != 0) {
        std::cout << "There is already a piece there!" << std::endl;
        inputAdd(state, history);
    } else {
        if (state.isTurnWhite) {
            state.whitePieces.set(position[0]);
        } else {
            state.blackPieces.set(position[0]);
        }
        state.isTurnWhite = !state.isTurnWhite;
        state.moveNumber ++;
        
        // Update empty neighbours map
        for (int neighbour : state.neighbors[position[0]]) {
            state.emptyNeighbors[neighbour].erase(position[0]);
        }
        
        checkPhase(state);
        history.saveState(state);
    }
}

// Removes a single piece from the board and overwrites the previous board state from history
void inputRemove(BoardState& state, History& history) {
    std::vector<int> position = runMillsBoard(state, 1);
    
    if (position[0] == -1) {
        std::cout << "Cannot go back now, please take a stone first!" << std::endl;
    } else if (position[0] == -2) {
        std::cout << "Cannot go back now, please take a stone first!" << std::endl;
    } else if (position[0] == -3) {
        exit(0);
    } else if (state.isTurnWhite & state.blackPieces[position[0]] != 1) {
        std::cout << "Please choose a black piece to remove!" << std::endl;
        inputRemove(state, history);
    } else if (!state.isTurnWhite & state.whitePieces[position[0]] != 1) {
        std::cout << "Please choose a white piece to remove!" << std::endl;
        inputRemove(state, history);
    } else {
        if (state.isTurnWhite) {
            state.blackPieces.reset(position[0]);
        } else {
            state.whitePieces.reset(position[0]);
        }
        state.isTurnWhite = !state.isTurnWhite;

        // Update empty neighbours map
        for (int neighbour : state.neighbors[position[0]]) {
            state.emptyNeighbors[neighbour].insert(position[0]);
        }

        checkPhase(state);
        history.deleteLastEntry();
        history.saveState(state);
    }
}

// Moves a piece on the board and appends that state to history
void inputMove(BoardState& state, History& history) {
    std::vector<int> position = runMillsBoard(state, 2);
    
    if (position[0] == -1) {
        std::vector<BoardState> hist = history.getHistory();
        try {
            state = hist.at(hist.size() - 2);
            history.deleteLastEntry();
        } catch (const std::out_of_range& e) {
            std::cout << "Not enough history to go back!" << std::endl;
        }
    } else if (position[0] == -2) {
        std::vector<BoardState> hist = history.getHistory();
        try {
            state = hist.at(hist.size() - 3);
            history.deleteLastEntry();
            history.deleteLastEntry();
        } catch (const std::out_of_range& e) {
            std::cout << "Not enough history to go back two steps!" << std::endl;
        }
    } else if (position[0] == -3) {
        exit(0);
    } else if (state.whitePieces[position[1]] != 0 || state.blackPieces[position[1]] != 0) {
        std::cout << "There is already a piece at the target location!" << std::endl;
        inputMove(state, history); 
    } else if ((state.isTurnWhite & state.whitePieces[position[0]] != 1) || (!state.isTurnWhite & state.blackPieces[position[0]] != 1)){
        std::cout << "There is none of your pieces at the origin!" << std::endl;
        inputMove(state, history); 
    } else {
        if (state.isTurnWhite) {
            state.whitePieces.reset(position[0]);
            state.whitePieces.set(position[1]);
        } else {
            state.blackPieces.reset(position[0]);
            state.blackPieces.set(position[1]);
        }
        state.isTurnWhite = !state.isTurnWhite;
        state.moveNumber ++;

        // Update empty neighbours map
        for (int neighbour : state.neighbors[position[0]]) {
            state.emptyNeighbors[neighbour].insert(position[0]);
        }
        for (int neighbour : state.neighbors[position[1]]) {
            state.emptyNeighbors[neighbour].erase(position[1]);
        }

        checkPhase(state);
        history.saveState(state);
    }
}