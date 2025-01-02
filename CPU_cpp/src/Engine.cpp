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
    for (const std::bitset<24>& mill : state.possibleMills) {
        if ((piecesToCheck & mill).count() == 3) {
            millCountBeforeMove ++;
        }
    }

    piecesToCheck.set(movedPieceIndex);
    int millCountAfterMove = 0;
    for (const std::bitset<24>& mill : state.possibleMills) {
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

// for a given board state count the number of closed mills for both colours
Colours countMill(const BoardState& state) {
    Colours result;

    for (const std::bitset<24>& mill : state.possibleMills) {
        if ((state.whitePieces & mill).count() == 3) {
            result.white ++;
        }
        if ((state.blackPieces & mill).count() == 3) {
            result.black ++;
        }
    }

    return result;
}

// for a given board state count the number of open mills for both colours
Colours countOpenMill(const BoardState& state) {
    Colours result;

    for (const std::bitset<24>& mill : state.possibleMills) {
        if ((state.whitePieces & mill).count() == 2 & !(state.blackPieces & mill).any()) {
            result.white ++;
        }
        if ((state.blackPieces & mill).count() == 2 & !(state.whitePieces & mill).any()) {
            result.black ++;
        }
    }

    return result;
}

// for a given board state count the number of double mills for both colours which are not blocked
Colours countDoubleMill(const BoardState& state) {
    Colours result;

    for (int i = 0; i < 16; i++)  {
        if ((state.whitePieces & state.possibleDoubleMills[i]).count() == 5 & !(state.blackPieces & state.doubleMillBlockers[i]).any()) {
            result.white ++;
        }
        if ((state.blackPieces & state.possibleDoubleMills[i]).count() == 5 & !(state.whitePieces & state.doubleMillBlockers[i]).any()) {
            result.white ++;
        }
    }

    return result;
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

Colours getPossibleMoveNumbers(const BoardState& state) {
    Colours result;
    result.white = 0;
    result.black = 0;
    int numberEmptySpaces = state.emptySpaces.count();
    
    if (state.isPlacingPhase) {
        result.white = numberEmptySpaces;
        result.black = numberEmptySpaces;
    } else {
        if (state.isFlyingPhaseWhite) {
            result.white = numberEmptySpaces;
        } else {
            for (int i = 0; i < 24; i++) { 
                if (state.whitePieces[i]) {
                    result.white += state.emptyNeighbors[i].size();
                }
            }
        }

        if (state.isFlyingPhaseBlack) {
            result.black = numberEmptySpaces;
        } else {
            for (int i = 0; i < 24; i++) { 
                if (state.blackPieces[i]) {
                    result.black += state.emptyNeighbors[i].size();
                }
            }
        }
    }
    
    return result;
}

Colours getPossibleMidGameMoveNumbers(const BoardState& state) {
    Colours result;
    
    for (int i = 0; i < 24; i++) { 
        if (state.whitePieces[i]) {
            result.white += state.emptyNeighbors[i].size();
        }
        if (state.blackPieces[i]) {
            result.black += state.emptyNeighbors[i].size();
        }
    }
    
    return result;
}

// Returns +1 if white has won, -1 if black has won and 0 if it is undecided
int isTerminalNode(const BoardState& state) {
    if (!state.isPlacingPhase) { // Winning during the placing phase is impossible
        // Win because of piece count
        if (state.blackPieces.count() < 3) {
            return 1;
        } else if (state.whitePieces.count() < 3) {
            return -1;
        }

        // Win because no more legal moves
        Colours availableMoves = getPossibleMoveNumbers(state);

        if (availableMoves.black == 0 & !state.isTurnWhite) { 
            return 1;
        } else if (availableMoves.white == 0 & state.isTurnWhite) { 
            return -1;
        }
    }

    return 0;
}

//Evaluates the position
//TODO: Change weightings based on the current phase of the game
//TODO: Change weightings based on which player's turn it is?
//TODO: Train these weightings with AI
float evaluate(const BoardState& state) {
    // Check if a playes has won (~0% of time)
    int isTerminal = isTerminalNode(state);
    if (isTerminal != 0) {
        return 9001. * isTerminal;
    }

    float score = 0.;

    // Modify score based on material and position (~10% of time)
    const int corners[] = {0, 2, 3, 5, 6, 8, 15, 17, 18, 20, 21, 23};
    const int threeCrossings[] = {1, 7, 9, 11, 12, 14, 16, 22};
    const int fourCrossings[] = {4, 10, 13, 19};

    for (int pos : corners) {
        if (state.whitePieces[pos]) {
            score += state.weights.corner;
        } else if (state.blackPieces[pos]) {
            score -= state.weights.corner;
        }
    }

    for (int pos : threeCrossings) {
        if (state.whitePieces[pos]) {
            score += state.weights.three_cross;
        } else if (state.blackPieces[pos]) {
            score -= state.weights.three_cross;
        }
    }

    for (int pos : fourCrossings) {
        if (state.whitePieces[pos]) {
            score += state.weights.four_cross;
        } else if (state.blackPieces[pos]) {
            score -= state.weights.four_cross;
        }
    }


    // Modify score based on (possible) mills in the position
    Colours millNumbersClosed = countMill(state); // ~20% of time
    score += (millNumbersClosed.white - millNumbersClosed.black) * state.weights.closed_mill;
    Colours millNumbersOpen = countOpenMill(state); // ~25% of time
    score += (millNumbersOpen.white - millNumbersOpen.black) * state.weights.open_mill;
    Colours millNumbersDouble = countDoubleMill(state); // ~25% of time
    score += (millNumbersDouble.white - millNumbersDouble.black) * state.weights.double_mill;




    // Modify score based on mobility of the pieces (not important if any player has flying phase)
    // Is important for the future game however if it's still early game
    if (!state.isFlyingPhaseWhite & !state.isFlyingPhaseBlack) {    // ~20% of time
        Colours possibleMoves = getPossibleMidGameMoveNumbers(state);
        score += (possibleMoves.white - possibleMoves.black) * state.weights.legal_moves;
    }

    return score;
}