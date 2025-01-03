#ifndef PLAYERVSMACHINE_H
#define PLAYERVSMACHINE_H

#include "Engine.h"
#include "GUI.h"
#include "UserInput.h"

void threadedMinimax(const BoardState& node, int depth, float alpha, float beta, bool maximizingPlayer, std::pair<float, BoardState>& result);

void playGame(bool isPlayerWhite, float maxComputationTime = 3., int maxCallDepth = 100, bool multiThreading = false, BoardState state = BoardState(), History history = History());

#endif // PLAYERVSMACHINE_H