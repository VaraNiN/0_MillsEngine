#include "Engine.h"
#include "GUI.h"
#include "UserInput.h"
#include <chrono>
#include <thread>
#include <iostream>
#include <thread>
#include <vector>
#include <functional>

void threadedMinimax(const BoardState& node, int depth, float alpha, float beta, bool maximizingPlayer, std::pair<float, BoardState>& result) {
    result = minimax(node, depth, alpha, beta, maximizingPlayer);
}


std::pair<float, BoardState> iterativeDeepening(const BoardState& state, float timeLimit, int maxDepth) {
    float bestEval = 0;
    float eval = 0;
    BoardState bestState = state;

    if (state.isPlayerWhite) {
        bestEval = 1e6;
    } else {
        bestEval = 1e6;
    }

    minimaxStart = std::chrono::steady_clock::now();

    for (int depth = 1; depth < maxDepth; depth++) {
        auto currentTime = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsedSeconds = currentTime - minimaxStart;

        BoardState currentState;
        std::tie(eval, currentState) = minimax(state, depth, -10000, 10000, !state.isPlayerWhite, generateKey(state), timeLimit);

        if (elapsedSeconds.count() >= timeLimit) {
            std::cout << "Time limit exceeded. Aborting search." << std::endl;
            break;
        }

        bestEval = eval;
        bestState = currentState;
    
        std::cout << "Depth: " << depth << ", Eval: " << eval << std::endl;
    }

    return {bestEval, bestState};
}

void playGame(bool isPlayerWhite, float maxComputationTime, int maxCallDepth, bool multiThreading, BoardState state, History history) {
    state.isPlayerWhite = isPlayerWhite;
    history.saveState(state);
    int currentPieces = state.whitePieces.count() + state.blackPieces.count();
    int previousPieces = state.whitePieces.count() + state.blackPieces.count();
    int turnsWithoutCapture = -1;

    while (true) {
        // Check if game has ended
        int outcome = isTerminalNode(state);
        if (outcome == 1) {
            print("White has won!");
        } else if (outcome == -1) {
            print("Black has won!");
        } else if (currentPieces != previousPieces) {
            turnsWithoutCapture = 0;
        } else {
            turnsWithoutCapture++;
            if (state.isFlyingPhaseWhite & state.isFlyingPhaseBlack & turnsWithoutCapture > 10 || turnsWithoutCapture > 50) {
                print("The game is a draw!");
                break;
            }
        }

        //show_position(state);

        // Input moves from human and computer
        if (state.isPlayerWhite == state.isTurnWhite) {
            playerMove(state, history);
        } else {
            callCount = 0;
            leafCount = 0;
            float eval;
            BoardState newState;

            auto start = std::chrono::high_resolution_clock::now();

            if (multiThreading) {   // Multi-Threading really goes against the alpha beta pruning and, at least naively implemented like here, is not worth it :(
                std::vector<BoardState> children = getChildren(state);
                std::vector<std::thread> threads;
                std::vector<std::pair<float, BoardState>> results(children.size());

                for (size_t i = 0; i < children.size(); ++i) {
                    threads.emplace_back(threadedMinimax, std::ref(children[i]), 4, -10000, 10000, state.isPlayerWhite, std::ref(results[i]));
                } 

                for (auto& thread : threads) {
                    thread.join();
                }

                if (state.isPlayerWhite) {
                    eval = 1e6;
                    for (int i = 0; i < results.size(); i++) {
                        if (results[i].first < eval ) {
                            eval = results[i].first;
                            newState = children[i];    // results of course include the best follow up move to the child, so we need to pick the child itself
                        }
                    } 
                } else {
                    eval = -1e6;
                    for (int i = 0; i < results.size(); i++) {
                        if (results[i].first > eval ) {
                            eval = results[i].first;
                            newState = children[i];
                        }
                    } 
                }
            } else {
                //std::tie(eval, newState) = minimax(state, 5, -10000, 10000, !state.isPlayerWhite);
                std::tie(eval, newState) = iterativeDeepening(state, maxComputationTime, maxCallDepth);
            }



            auto end = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> duration = end - start;

            std::cout << "There were " << callCount << " minimax calls (" << leafCount << " leafs) taking " << duration.count() << " seconds \n";
            std::cout << "Average call length: " << 1e6 * duration.count() / callCount << " µs\n";
            std::cout << "The current evaluation is: " << eval << "\n\n";

            checkValidity(newState);
            state = newState;
            history.saveState(state);
        }
    }
}