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
        key[1] = state.isPlacingPhase;
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
    state.isPlacingPhase = (state.moveNumber < 18);

    if (!state.isPlacingPhase) {
        state.isFlyingPhaseWhite = (state.whitePieces.count() == 3);
        state.isFlyingPhaseBlack = (state.blackPieces.count() == 3);
    }
}

// for a given board state and move of current colour, returns a bool telling if that move formed a mill
bool checkMill(const BoardState& state, int movedPieceIndex) {
    std::bitset<24> piecesToCheck;
    if (state.isTurnWhite) {
        piecesToCheck = state.whitePieces;
    } else {
        piecesToCheck = state.blackPieces;
    }

    int millCountBeforeMove = 0;
    for (std::bitset<24> mill : state.possibleMills) {
        if ((piecesToCheck & mill).count() == 3) {
            millCountBeforeMove ++;
        }
    }

    piecesToCheck.set(movedPieceIndex);
    int millCountAfterMove = 0;
    for (std::bitset<24> mill : state.possibleMills) {
        if ((piecesToCheck & mill).count() == 3) {
            millCountAfterMove ++;
        }
    }

    if (millCountAfterMove > millCountBeforeMove) {
        return true;
    } else {
        return false;
    }
}

// returns vector with all options for pieces of the non current colour being removed
std::vector<BoardState> removePieces(const BoardState& state) {
    std::vector<BoardState> children;
    BoardState dummyState = state;
    for (int i = 0; i < 24; i++) {
        if (state.blackPieces[i] & state.isTurnWhite || state.whitePieces[i] & !state.isTurnWhite) {
            if (state.isTurnWhite) {
                dummyState.blackPieces.reset(i);
            } else {
                dummyState.whitePieces.reset(i);
            }
            dummyState.emptySpaces.set(i);
            for (int neighbour : state.neighbors[i]) {
                dummyState.emptyNeighbors[neighbour].insert(i);
            }     
            dummyState.isTurnWhite = !dummyState.isTurnWhite;
            checkPhase(dummyState);
            children.push_back(dummyState);
            dummyState = state;
        }
    }
    return children;
}

//Returns all possible moves given a specific position
//TODO: Write this more concisely
std::vector<BoardState> getChildren(const BoardState& state) {
    std::vector<BoardState> children;
    std::vector<BoardState> removedChildren;
    BoardState dummyState = state;
    bool madeMill;

    if (state.isPlacingPhase) {
        for (int i = 0; i < 24; i++) {
            if (state.emptySpaces[i]) {
                madeMill = checkMill(state, i);
                if (state.isTurnWhite) {
                    dummyState.whitePieces.set(i);
                } else {
                    dummyState.blackPieces.set(i);
                }
                dummyState.emptySpaces.reset(i);
                dummyState.moveNumber ++;
                for (int neighbour : state.neighbors[i]) {
                    dummyState.emptyNeighbors[neighbour].erase(i);
                }
                
                if (madeMill) {
                    removedChildren = removePieces(dummyState);
                    children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                } else {
                    dummyState.isTurnWhite = !dummyState.isTurnWhite;
                    checkPhase(dummyState);
                    children.push_back(dummyState);
                }
                dummyState = state;
            }
        }
    } else if (state.isTurnWhite & state.isFlyingPhaseWhite) {
        for (int i = 0; i < 24; i++) {
            if (state.whitePieces[i]) {
                for (int j = 0; j < 24; j++) {
                    if (state.emptySpaces[j]) {
                        madeMill = checkMill(state, j);
                        print(madeMill);
                        dummyState.whitePieces.reset(i);
                        dummyState.whitePieces.set(j);
                        dummyState.emptySpaces.set(i);
                        dummyState.emptySpaces.reset(j);
                        dummyState.moveNumber ++;

                        for (int neighbour : state.neighbors[i]) {
                            dummyState.emptyNeighbors[neighbour].insert(i);
                        }       
                        for (int neighbour : state.neighbors[j]) {
                            dummyState.emptyNeighbors[neighbour].erase(j);
                        }        

                        if (madeMill) {
                            removedChildren = removePieces(dummyState);
                            children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                        } else {
                            dummyState.isTurnWhite = !dummyState.isTurnWhite;
                            checkPhase(dummyState);
                            children.push_back(dummyState);
                        }

                        dummyState = state;
                    }
                }
            }
        }
    } else if (!state.isTurnWhite & state.isFlyingPhaseBlack) {
        for (int i = 0; i < 24; i++) {
            if (state.blackPieces[i]) {
                for (int j = 0; j < 24; j++) {
                    if (state.emptySpaces[j]) {
                        madeMill = checkMill(state, j);
                        dummyState.blackPieces.reset(i);
                        dummyState.blackPieces.set(j);
                        dummyState.emptySpaces.set(i);
                        dummyState.emptySpaces.reset(j);
                        dummyState.moveNumber ++;

                        for (int neighbour : state.neighbors[i]) {
                            dummyState.emptyNeighbors[neighbour].insert(i);
                        }       
                        for (int neighbour : state.neighbors[j]) {
                            dummyState.emptyNeighbors[neighbour].erase(j);
                        }        

                        if (madeMill) {
                            removedChildren = removePieces(dummyState);
                            children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                        } else {
                            dummyState.isTurnWhite = !dummyState.isTurnWhite;
                            checkPhase(dummyState);
                            children.push_back(dummyState);
                        }

                        dummyState = state;
                    }
                }
            }
        }
    } else if (state.isTurnWhite) {
        for (int i = 0; i < 24; i++) {
            if (state.whitePieces[i]) {
                for (int emptyNeighbor : state.emptyNeighbors[i]) {
                    madeMill = checkMill(state, emptyNeighbor);
                    dummyState.whitePieces.reset(i);
                    dummyState.whitePieces.set(emptyNeighbor);
                    dummyState.emptySpaces.set(i);
                    dummyState.emptySpaces.reset(emptyNeighbor);
                    dummyState.moveNumber ++;
                    for (int neighbour : state.neighbors[i]) {
                        dummyState.emptyNeighbors[neighbour].insert(i);
                    }       
                    for (int neighbour : state.neighbors[emptyNeighbor]) {
                        dummyState.emptyNeighbors[neighbour].erase(emptyNeighbor);
                    }  

                    if (madeMill) {
                        removedChildren = removePieces(dummyState);
                        children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                    }  else {
                        dummyState.isTurnWhite = !dummyState.isTurnWhite;
                        checkPhase(dummyState);
                        children.push_back(dummyState);
                    }

                    dummyState = state;
                }
            }
        }
    } else {
        for (int i = 0; i < 24; i++) {
            if (state.blackPieces[i]) {
                for (int emptyNeighbor : state.emptyNeighbors[i]) {
                    madeMill = checkMill(state, emptyNeighbor);
                    dummyState.blackPieces.reset(i);
                    dummyState.blackPieces.set(emptyNeighbor);
                    dummyState.emptySpaces.set(i);
                    dummyState.emptySpaces.reset(emptyNeighbor);
                    dummyState.moveNumber ++;
                    for (int neighbour : state.neighbors[i]) {
                        dummyState.emptyNeighbors[neighbour].insert(i);
                    }       
                    for (int neighbour : state.neighbors[emptyNeighbor]) {
                        dummyState.emptyNeighbors[neighbour].erase(emptyNeighbor);
                    }  

                    if (madeMill) {
                        removedChildren = removePieces(dummyState);
                        children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                    } else {
                        dummyState.isTurnWhite = !dummyState.isTurnWhite;
                        checkPhase(dummyState);
                        children.push_back(dummyState);
                    }

                    dummyState = state;
                }
            }
        }

    }

    return children;
}