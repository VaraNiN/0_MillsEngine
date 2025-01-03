#include "Engine.h"
#include "GUI.h"
#include <bitset>
#include <string>
#include <sstream>
#include <vector>
#include <cstdint>
#include <iostream>
#include <cstdlib>

// Adds a single piece to the board and appends that state to history
int inputAdd(BoardState& state, History& history) {
    std::vector<int> position = runMillsBoard(state, 1);
    
    if (position[0] == -1) {
        std::vector<BoardState> hist = history.getHistory();
        try {
            bool playerColour = state.isPlayerWhite;
            state = hist.at(hist.size() - 2);
            history.deleteLastEntry();
            state.isPlayerWhite = !playerColour;
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
    } else if (state.whitePieces[position[0]] || state.blackPieces[position[0]]) {
        std::cout << "There is already a piece there!" << std::endl;
    } else {
        if (state.isTurnWhite) {
            state.whitePieces.set(position[0]);
        } else {
            state.blackPieces.set(position[0]);
        }
        state.emptySpaces.reset(position[0]);
        bool formedMill = checkMill(state, position[0]);
        state.moveNumber ++;
        state.isTurnWhite ^= true;
        
        // Update empty neighbours map
        for (int neighbour : gameInfo.neighbors[position[0]]) {
            state.emptyNeighbors[neighbour].reset(position[0]);
        }
        
        checkPhase(state);
        history.saveState(state);
        if (formedMill) {
            return 1;
        } else {
            return 0;
        }
    }
    return -1;
}

// Removes a single piece from the board and overwrites the previous board state from history
void inputRemove(BoardState& state, History& history) {
    state.isTurnWhite ^= true;
    std::vector<int> position = runMillsBoard(state, 1);
    
    if (position[0] == -1) {
        std::cout << "Cannot go back now, please take a stone first!" << std::endl;
        inputRemove(state, history);
    } else if (position[0] == -2) {
        std::cout << "Cannot go back now, please take a stone first!" << std::endl;
        inputRemove(state, history);
    } else if (position[0] == -3) {
        exit(0);
    } else if (state.isTurnWhite & !state.blackPieces[position[0]]) {
        std::cout << "Please choose a black piece to remove!" << std::endl;
        inputRemove(state, history);
    } else if (!state.isTurnWhite & !state.whitePieces[position[0]]) {
        std::cout << "Please choose a white piece to remove!" << std::endl;
        inputRemove(state, history);
    } else {
        if (state.isTurnWhite) {
            state.blackPieces.reset(position[0]);
            state.emptySpaces.set(position[0]);
        } else {
            state.whitePieces.reset(position[0]);
            state.emptySpaces.set(position[0]);
        }
        state.isTurnWhite ^= true;

        // Update empty neighbours map
        for (int neighbour : gameInfo.neighbors[position[0]]) {
            state.emptyNeighbors[neighbour].set(position[0]);
        }

        checkPhase(state);
        history.deleteLastEntry();
        history.saveState(state);
    }
}

// Moves a piece on the board and appends that state to history
int inputMove(BoardState& state, History& history) {
    std::vector<int> position = runMillsBoard(state, 2);
    
    if (position[0] == -1) {
        std::vector<BoardState> hist = history.getHistory();
        try {
            bool playerColour = state.isPlayerWhite;
            state = hist.at(hist.size() - 2);
            history.deleteLastEntry();
            state.isPlayerWhite = !playerColour;
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
    } else if (state.whitePieces[position[1]] || state.blackPieces[position[1]]) {
        std::cout << "There is already a piece at the target location!" << std::endl;
    } else if ((state.isTurnWhite & !state.whitePieces[position[0]]) || (!state.isTurnWhite & !state.blackPieces[position[0]])){
        std::cout << "There is none of your pieces at the origin!" << std::endl;
    } else if (state.isTurnWhite & !state.isFlyingPhaseWhite & !state.emptyNeighbors[position[0]][position[1]] || 
              !state.isTurnWhite & !state.isFlyingPhaseBlack & !state.emptyNeighbors[position[0]][position[1]]) {
                    std::cout << "Cannot reach target from origin!" << std::endl;
    } else {
        if (state.isTurnWhite) {
            state.whitePieces.reset(position[0]);
            state.whitePieces.set(position[1]);
            state.emptySpaces.set(position[0]);
            state.emptySpaces.reset(position[1]);
        } else {
            state.blackPieces.reset(position[0]);
            state.blackPieces.set(position[1]);
            state.emptySpaces.set(position[0]);
            state.emptySpaces.reset(position[1]);
        }
        bool formedMill = checkMill(state, position[1]);
        state.moveNumber ++;
        state.isTurnWhite ^= true;

        // Update empty neighbours map
        for (int neighbour : gameInfo.neighbors[position[0]]) {
            state.emptyNeighbors[neighbour].set(position[0]);
        }
        for (int neighbour : gameInfo.neighbors[position[1]]) {
            state.emptyNeighbors[neighbour].reset(position[1]);
        }

        checkPhase(state);
        history.saveState(state);
        if (formedMill) {
            return 1;
        } else {
            return 0;
        }
    }
    return -1;
}


void playerMove(BoardState& state, History& history) {
    int gameState;
    if (state.isPlacingPhase) {
        gameState = inputAdd(state, history);
    } else {
        gameState = inputMove(state, history);
    }

    if (gameState == -1) { // if player did not put in move correctly or pressed a go back button
        playerMove(state, history);
    } else {
        if (gameState == 1) {
            inputRemove(state, history);
        }
        checkValidity(state);
    }
}