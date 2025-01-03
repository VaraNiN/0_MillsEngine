#include "Engine.h"
#include "GUI.h"
#include <bitset>
#include <string>
#include <sstream>
#include <vector>
#include <cstdint>
#include <iostream>
#include <cstdlib>
#include <algorithm> 
#include <utility>
#include <unordered_map>
#include <mutex>

GameInfo gameInfo;
EvaluationWeights evalWeights;

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
        print(state.whitePieces);
        print(state.blackPieces);
        throw std::runtime_error("Error: Two pieces occupy the same position!");
    } else if ((state.whitePieces & state.emptySpaces).any()) {
        print(state.whitePieces);
        print(state.emptySpaces);
        throw std::runtime_error("Error: Empty spaces are set wrong!");
    } else if ((state.blackPieces & state.emptySpaces).any()) {
        print(state.blackPieces);
        print(state.emptySpaces);
        throw std::runtime_error("Error: Empty spaces are set wrong!");
    } /* else {
        std::cout << "Boardstate is valid!" << std::endl;
    } */
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
bool checkMill(const BoardState& state, int pos) {
    const auto& pieces = state.isTurnWhite ? state.whitePieces : state.blackPieces;
    return (pieces & gameInfo.possibleMillsPerPosition[2 * pos]).count() == 3 || 
           (pieces & gameInfo.possibleMillsPerPosition[2 * pos + 1]).count() == 3;
}

// for a given board state count the number of closed mills for both colours
Colours countMill(const BoardState& state) {
    Colours result;

    for (const std::bitset<24>& mill : gameInfo.possibleMills) {
        if ((state.whitePieces & mill).count() == 3) {
            result.white++;
        }
        if ((state.blackPieces & mill).count() == 3) {
            result.black++;
        }
    }

    return result;
}

// for a given board state count the number of open mills for both colours
Colours countOpenMill(const BoardState& state) {
    Colours result;

    for (const std::bitset<24>& mill : gameInfo.possibleMills) {
        if ((state.whitePieces & mill).count() == 2 & !(state.blackPieces & mill).any()) {
            result.white++;
        }
        if ((state.blackPieces & mill).count() == 2 & !(state.whitePieces & mill).any()) {
            result.black++;
        }
    }

    return result;
}

// for a given board state count the number of double mills for both colours which are not blocked
Colours countDoubleMill(const BoardState& state) {
    Colours result;

    for (int i = 0; i < 16; i++)  {
        if ((state.whitePieces & gameInfo.possibleDoubleMills[i]).count() == 5 & !(state.blackPieces & gameInfo.doubleMillBlockers[i]).any()) {
            result.white++;
        }
        if ((state.blackPieces & gameInfo.possibleDoubleMills[i]).count() == 5 & !(state.whitePieces & gameInfo.doubleMillBlockers[i]).any()) {
            result.white++;
        }
    }

    return result;
}

// returns vector with all options for pieces of the non current colour being removed
std::vector<BoardState> removePieces(const BoardState& state) {
    std::vector<BoardState> children;
    children.reserve(9);
    BoardState dummyState = state;
    for (int i = 0; i < 24; i++) {
        if (state.blackPieces[i] & state.isTurnWhite || state.whitePieces[i] & !state.isTurnWhite) {
            if (state.isTurnWhite) {
                dummyState.blackPieces.reset(i);
            } else {
                dummyState.whitePieces.reset(i);
            }
            dummyState.emptySpaces.set(i);
            for (int neighbour : gameInfo.neighbors[i]) {
                dummyState.emptyNeighbors[neighbour].reset(i);
            }     
            dummyState.isTurnWhite = !dummyState.isTurnWhite;
            checkPhase(dummyState);
            children.emplace_back(dummyState);
            dummyState = state;
            //dummyState.whitePieces = state.whitePieces;
            //dummyState.blackPieces = state.blackPieces;
            //dummyState.emptySpaces = state.emptySpaces;
            //dummyState.emptyNeighbors = state.emptyNeighbors;
            //dummyState.isTurnWhite ^= true;
        }
    }
    return children;
}

//Returns all possible moves given a specific position
//TODO: Write this more concisely
std::vector<BoardState> getChildren(const BoardState& state) {
    std::vector<BoardState> children;
    children.reserve(100);
    std::vector<BoardState> removedChildren;
    children.reserve(9);
    BoardState dummyState = state;

    if (state.isPlacingPhase) {
        for (int i = 0; i < 24; i++) {
            if (state.emptySpaces[i]) {
                if (state.isTurnWhite) {
                    dummyState.whitePieces.set(i);
                } else {
                    dummyState.blackPieces.set(i);
                }
                dummyState.emptySpaces.reset(i);
                dummyState.moveNumber++;
                for (int neighbour : gameInfo.neighbors[i]) {
                    dummyState.emptyNeighbors[neighbour].reset(i);
                }
                
                if (checkMill(state, i)) {
                    removedChildren = removePieces(dummyState);
                    children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                } else {
                    dummyState.isTurnWhite ^= true;
                    checkPhase(dummyState);
                    children.emplace_back(dummyState);
                }
                dummyState = state;
                //dummyState.whitePieces = state.whitePieces;
                //dummyState.blackPieces = state.blackPieces;
                //dummyState.emptySpaces = state.emptySpaces;
                //dummyState.moveNumber = state.moveNumber;
                //dummyState.emptyNeighbors = state.emptyNeighbors;
                //dummyState.isTurnWhite ^= true;
            }
        }
    } else if (state.isTurnWhite & state.isFlyingPhaseWhite) {
        for (int i = 0; i < 24; i++) {
            if (state.whitePieces[i]) {
                for (int j = 0; j < 24; j++) {
                    if (state.emptySpaces[j]) {
                        dummyState.whitePieces.reset(i);
                        dummyState.whitePieces.set(j);
                        dummyState.emptySpaces.set(i);
                        dummyState.emptySpaces.reset(j);
                        dummyState.moveNumber++;

                        for (int neighbour : gameInfo.neighbors[i]) {
                            dummyState.emptyNeighbors[neighbour].set(i);
                        }       
                        for (int neighbour : gameInfo.neighbors[j]) {
                            dummyState.emptyNeighbors[neighbour].reset(j);
                        }        

                        if (checkMill(state, j)) {
                            removedChildren = removePieces(dummyState);
                            children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                        } else {
                            dummyState.isTurnWhite = !dummyState.isTurnWhite;
                            checkPhase(dummyState);
                            children.emplace_back(dummyState);
                        }

                        dummyState = state;
                        //dummyState.whitePieces = state.whitePieces;
                        //dummyState.blackPieces = state.blackPieces;
                        //dummyState.emptySpaces = state.emptySpaces;
                        //dummyState.moveNumber = state.moveNumber;
                        //dummyState.emptyNeighbors = state.emptyNeighbors;
                        //dummyState.isTurnWhite ^= true;
                    }
                }
            }
        }
    } else if (!state.isTurnWhite & state.isFlyingPhaseBlack) {
        for (int i = 0; i < 24; i++) {
            if (state.blackPieces[i]) {
                for (int j = 0; j < 24; j++) {
                    if (state.emptySpaces[j]) {
                        dummyState.blackPieces.reset(i);
                        dummyState.blackPieces.set(j);
                        dummyState.emptySpaces.set(i);
                        dummyState.emptySpaces.reset(j);
                        dummyState.moveNumber++;

                        for (int neighbour : gameInfo.neighbors[i]) {
                            dummyState.emptyNeighbors[neighbour].set(i);
                        }       
                        for (int neighbour : gameInfo.neighbors[j]) {
                            dummyState.emptyNeighbors[neighbour].reset(j);
                        }           

                        if (checkMill(state, j)) {
                            removedChildren = removePieces(dummyState);
                            children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                        } else {
                            dummyState.isTurnWhite = !dummyState.isTurnWhite;
                            checkPhase(dummyState);
                            children.emplace_back(dummyState);
                        }

                        dummyState = state;
                        //dummyState.whitePieces = state.whitePieces;
                        //dummyState.blackPieces = state.blackPieces;
                        //dummyState.emptySpaces = state.emptySpaces;
                        //dummyState.moveNumber = state.moveNumber;
                        //dummyState.emptyNeighbors = state.emptyNeighbors;
                        //dummyState.isTurnWhite ^= true;
                    }
                }
            }
        }
    } else if (state.isTurnWhite) {
        for (int i = 0; i < 24; i++) {
            if (state.whitePieces[i]) {
                for (int j = 0; j < 24; j++) {
                    if (state.emptyNeighbors[i][j]) {
                        dummyState.whitePieces.reset(i);
                        dummyState.whitePieces.set(j);
                        dummyState.emptySpaces.set(i);
                        dummyState.emptySpaces.reset(j);
                        dummyState.moveNumber++;
                        for (int neighbour : gameInfo.neighbors[i]) {
                            dummyState.emptyNeighbors[neighbour].set(i);
                        }       
                        for (int neighbour : gameInfo.neighbors[j]) {
                            dummyState.emptyNeighbors[neighbour].reset(j);
                        }  

                        if (checkMill(state, j)) {
                            removedChildren = removePieces(dummyState);
                            children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                        }  else {
                            dummyState.isTurnWhite = !dummyState.isTurnWhite;
                            checkPhase(dummyState);
                            children.emplace_back(dummyState);
                        }

                        dummyState = state;
                        //dummyState.whitePieces = state.whitePieces;
                        //dummyState.blackPieces = state.blackPieces;
                        //dummyState.emptySpaces = state.emptySpaces;
                        //dummyState.moveNumber = state.moveNumber;
                        //dummyState.emptyNeighbors = state.emptyNeighbors;
                        //dummyState.isTurnWhite ^= true;
                    }
                }
            }
        }
    } else {
        for (int i = 0; i < 24; i++) {
            if (state.blackPieces[i]) {
                for (int j = 0; j < 24; j++) {
                    if (state.emptyNeighbors[i][j]) {
                        dummyState.blackPieces.reset(i);
                        dummyState.blackPieces.set(j);
                        dummyState.emptySpaces.set(i);
                        dummyState.emptySpaces.reset(j);
                        dummyState.moveNumber++;
                        for (int neighbour : gameInfo.neighbors[i]) {
                            dummyState.emptyNeighbors[neighbour].set(i);
                        }       
                        for (int neighbour : gameInfo.neighbors[j]) {
                            dummyState.emptyNeighbors[neighbour].reset(j);
                        }  

                        if (checkMill(state, j)) {
                            removedChildren = removePieces(dummyState);
                            children.insert(children.end(), removedChildren.begin(), removedChildren.end());
                        }  else {
                            dummyState.isTurnWhite = !dummyState.isTurnWhite;
                            checkPhase(dummyState);
                            children.emplace_back(dummyState);
                        }

                        dummyState = state;
                        //dummyState.whitePieces = state.whitePieces;
                        //dummyState.blackPieces = state.blackPieces;
                        //dummyState.emptySpaces = state.emptySpaces;
                        //dummyState.moveNumber = state.moveNumber;
                        //dummyState.emptyNeighbors = state.emptyNeighbors;
                        //dummyState.isTurnWhite ^= true;
                    }
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
                    result.white += state.emptyNeighbors[i].count();
                }
            }
        }

        if (state.isFlyingPhaseBlack) {
            result.black = numberEmptySpaces;
        } else {
            for (int i = 0; i < 24; i++) { 
                if (state.blackPieces[i]) {
                    result.black += state.emptyNeighbors[i].count();
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
            result.white += state.emptyNeighbors[i].count();
        }
        if (state.blackPieces[i]) {
            result.black += state.emptyNeighbors[i].count();
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

//Get the score based on the material on the board, weighted by position
float scoreFromMaterial (const BoardState& state) {
    float score = 0.;

    const int corners[] = {0, 2, 3, 5, 6, 8, 15, 17, 18, 20, 21, 23};
    const int threeCrossings[] = {1, 7, 9, 11, 12, 14, 16, 22};
    const int fourCrossings[] = {4, 10, 13, 19};

    for (int pos : corners) {
        if (state.whitePieces[pos]) {
            score += evalWeights.corner;
        } else if (state.blackPieces[pos]) {
            score -= evalWeights.corner;
        }
    }

    for (int pos : threeCrossings) {
        if (state.whitePieces[pos]) {
            score += evalWeights.three_cross;
        } else if (state.blackPieces[pos]) {
            score -= evalWeights.three_cross;
        }
    }

    for (int pos : fourCrossings) {
        if (state.whitePieces[pos]) {
            score += evalWeights.four_cross;
        } else if (state.blackPieces[pos]) {
            score -= evalWeights.four_cross;
        }
    }
    
    return score;
}


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

//Evaluates the position
//TODO: Change weightings based on the current phase of the game
//TODO: Change weightings based on which player's turn it is?
//TODO: Train these weightings with AI
float evaluate(const BoardState& state) {

    // Check if a playes has won (~5% of time)
    int isTerminal = isTerminalNode(state);
    if (isTerminal != 0 || state.isFlyingPhaseWhite || state.isFlyingPhaseBlack) {    // Severely simplify evaluation function on the endgame to cope with huge search space
        return 9001. * isTerminal + state.whitePieces.count() - state.blackPieces.count();
    }


    // Modify score based on material and position (~15% of time)
    float score = scoreFromMaterial(state);


    // Modify score based on (possible) mills in the position
    Colours millNumbersClosed = countMill(state); // ~15% of time
    score += (millNumbersClosed.white - millNumbersClosed.black) * evalWeights.closed_mill;
    Colours millNumbersOpen = countOpenMill(state); // ~25% of time
    score += (millNumbersOpen.white - millNumbersOpen.black) * evalWeights.open_mill;
    Colours millNumbersDouble = countDoubleMill(state); // ~25% of time
    score += (millNumbersDouble.white - millNumbersDouble.black) * evalWeights.double_mill;


    // Modify score based on mobility of the pieces   // ~15% of time
    Colours possibleMoves = getPossibleMidGameMoveNumbers(state);
    score += (possibleMoves.white - possibleMoves.black) * evalWeights.legal_moves;

    return score;
}

int callCount = 0;
int leafCount = 0;

std::unordered_map<std::bitset<50>, std::pair<float, int>> lookupTable;
std::mutex lookupTableMutex;


std::pair<float, BoardState> minimax(const BoardState& node, int depth, float alpha, float beta, bool maximizingPlayer) {   
    callCount++;

    std::bitset<50> key = generateKey(node);

    {
        std::lock_guard<std::mutex> guard(lookupTableMutex);
        if (lookupTable.find(key) != lookupTable.end() && lookupTable[key].second >= depth) {
            return {lookupTable[key].first, node};
        }
    }

    if (depth == 0 || isTerminalNode(node) != 0) {
        leafCount++;
        float eval = evaluate(node);
        {
            std::lock_guard<std::mutex> guard(lookupTableMutex);
            lookupTable[key] = {eval, depth};
        }
        return {eval, node};
    }

    BoardState bestNode;

    std::vector<BoardState> children = getChildren(node);
    std::vector<std::pair<float, BoardState>> evaluatedChildren; // evaluation, child

    for (const BoardState& child : children) {
        std::bitset<50> childKey = generateKey(child);
        float childEval;
        {
            std::lock_guard<std::mutex> guard(lookupTableMutex);
            if (lookupTable.find(childKey) != lookupTable.end()) {
                childEval = lookupTable[childKey].first;
            } else {
                childEval = evaluate(child);
                lookupTable[childKey] = {childEval, 0};
            }
        }
        evaluatedChildren.push_back({childEval, child});
    }

    if (maximizingPlayer) {
        float maxEval = -1e6;
        std::sort(evaluatedChildren.begin(), evaluatedChildren.end(), [](auto &left, auto &right) {
            return left.first > right.first; //Maximizing player wants highest eval moves first
        });  
        for (const auto& [dummy1, child] : evaluatedChildren) {
            auto [eval, dummy2] = minimax(child, depth - 1, alpha, beta, false);
            if (eval > maxEval) {
                maxEval = eval;
                bestNode = child;
            }
            alpha = std::max(alpha, eval);
            if (beta <= alpha)
                break; // Beta cut-off
        }
        {
            std::lock_guard<std::mutex> guard(lookupTableMutex);
            lookupTable[key] = {maxEval, depth};
        }
        return {maxEval, bestNode};
    } else {
        float minEval = 1e6;
        std::sort(evaluatedChildren.begin(), evaluatedChildren.end(), [](auto &left, auto &right) {
            return left.first < right.first; //Minimizing player wants lowest eval moves first
        });
        for (const auto& [dummy1, child] : evaluatedChildren) {
            auto [eval,dummy2] = minimax(child, depth - 1, alpha, beta, true);
            if (eval < minEval) {
                minEval = eval;
                bestNode = child;
            }
            beta = std::min(beta, eval);
            if (beta <= alpha)
                break; // Alpha cut-off
        }
        {
            std::lock_guard<std::mutex> guard(lookupTableMutex);
            lookupTable[key] = {minEval, depth};
        }
        return {minEval, bestNode};
    }
}