// Game -> Board -> Square

import { useState } from 'react';

function Square({ value, onSquareClick }) {
  return (
  <button className="square" onClick={onSquareClick}>
    {value}
  </button>
  );
}

function Board({ xIsNext, squares, onPlay }) {
  function handleClick(i) {
    if (calculateWinner(squares) || squares[i]) {
      return;
    }
    const nextSquares = squares.slice();
    if (xIsNext) {
      nextSquares[i] = "X";
    } else {
      nextSquares[i] = "O";
    }
    onPlay(nextSquares);
  } 

  const winner = calculateWinner(squares);
  let status;
  if (winner) {
    status = "Winner: " + winner;
  } else {
    status = "Next player: " + (xIsNext ? "X" : "O");
  }

  let squareCounter = 0;

  return (
    <>
      <div className="status">{status}</div>

      {Array.from({ length:3 }).map((_, i) => (
        <div key={i} className="board-row">
          {Array.from({ length:3 }).map((_, j) => {
            const index = i*3+j;
            return ( <Square key={j} value={squares[index]} onSquareClick={() => handleClick(index)} />);
          })}
        </div>
      ))}
   </>
  );
}

export default function Game() {
  const [history, setHistory] = useState([Array(9).fill(null)]);
  const [currentMove, setCurrentMove] = useState(0);
  const xIsNext = currentMove % 2 == 0;
  const currentSquares = history[currentMove]; 

  function handlePlay(nextSquares) {
    const nextHistory = [...history.slice(0, currentMove + 1), nextSquares];
    setHistory(nextHistory);
    setCurrentMove(nextHistory.length - 1);
  }

  // nextMove: これから currentMove に設定される値。ジャンプする回の盤面。
  function jumpTo(nextMove) {
    setCurrentMove(nextMove);
  }

  const moves = history.map((_, move) => {
    let description;
    if (move > 0) {
      description = `Go to move ${move}`;
    } else {
      description = 'Go to game start';
    }
    return (
      <li key={move}>
        {move === currentMove ? <div>You are at move #{move}</div> : <button onClick={() => jumpTo(move)}>{description}</button>}
      </li>
    ); 
  });

  console.debug(currentSquares);

  return (
    <div className="game">
      <div className="game-board">
        <Board xIsNext={xIsNext} squares={currentSquares} onPlay={handlePlay} />
      </div>
      <div className="game-info">
        <ol>{moves}</ol>
      </div>
    </div>
  );
} 

function calculateWinner(squares) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
  ];
  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i];
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
   }
   return null;
}

