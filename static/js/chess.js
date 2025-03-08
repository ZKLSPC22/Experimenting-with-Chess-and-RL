function convertIndex(index, color) {
    return color === 'white'? index : 63 - index;
}

const pieceIcons = {
    'P': '♙', 'p': '♟',
    'R': '♖', 'r': '♜',
    'N': '♘', 'n': '♞',
    'B': '♗', 'b': '♝',
    'Q': '♕', 'q': '♛',
    'K': '♔', 'k': '♚'
};

let selectedSquare = null;
let selectedSquareElement = null; // Track the selected square's DOM element
let squares = [];

function getCoordinatesFromIndex(index) {
    const row = Math.floor(index / 8);
    const col = index % 8;
    return [row, col];
}

function getIndexFromCoordinates(coords) {
    const [row, col] = coords;
    return row * 8 + col;
}

async function handleSquareClick(event) {
    var squareIndex = Array.from(squares).indexOf(event.target);
    if (squareIndex === -1) return;

    squareIndex = convertIndex(squareIndex, bottomColor);
    const coords = getCoordinatesFromIndex(squareIndex);

    if (!selectedSquare) {
        // First click: select piece
        const piece = getPieceAt(coords);
        if (piece) {
            // Clear any existing selection first
            if (selectedSquareElement) {
                selectedSquareElement.style.border = '';
            }
            
            selectedSquare = coords;
            selectedSquareElement = event.target;
            event.target.style.border = '2px solid red';
            await highlightValidMoves(coords);
        }
    } else {
        // Second click: attempt move
        const start = selectedSquare;
        const end = coords;
        
        // Clear highlights and selection immediately
        clearSquareHighlights();
        if (selectedSquareElement) {
            selectedSquareElement.style.border = '';
        }
        selectedSquare = null;
        selectedSquareElement = null;

        try {
            const response = await fetch('/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start: start, end: end })
            });
            const data = await response.json();
            if (data.status === 'success') {
                updateBoard();
                handleGameEnd(data);
            } else {
                alert('Invalid move!');
                // Re-enable selection if move failed
                await updateBoard();
            }
        } catch (error) {
            console.error('Error making move:', error);
            await updateBoard();
        }
    }
}

let Board = [];

// Fetch the board state from the server and update the display.
async function updateBoard() {
    try {
        const response = await fetch('/board');
        const data = await response.json();
        board = data.board;
        console.log('Board state from server:', board);  // 调试信息
        squares.forEach((square, index) => {
            index = convertIndex(index, bottomColor);
            const [row, col] = getCoordinatesFromIndex(index);
            const piece = board[row][col];
            if (piece === '.' || piece === '') {
                square.textContent = '';
                square.style.color = ''; // Reset color if empty.
            } else {
                square.textContent = pieceIcons[piece] || piece;
                square.style.color = (piece === piece.toLowerCase()) ? 'black' : 'white';
            }
        });
    } catch (error) {
        console.error('Error updating board:', error);
    }
}

function handleGameEnd(response) {
if (response.game_over) {
    if (response.message.includes('Checkmate')) {
    alert(response.message);
    } else if (response.message === 'Stalemate!') {
    alert(response.message);
    }
    // 禁用进一步的移动
    squares.forEach(square => square.removeEventListener('click', handleSquareClick));
}
}

// Highlight valid moves and disable invalid squares.

function clearSquareHighlights() {
    squares.forEach(square => {
        // Do not clear the selected square's border
        if (square !== selectedSquareElement) {
            square.style.border = '';
        }
        square.classList.remove('highlight');
    });
}

async function highlightValidMoves(start) {
    try {
        const response = await fetch('/get_possible_moves', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start: start })
        });
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        console.log('Possible moves from', start, ':', data.moves);
        
        data.moves.forEach(move => {
            var index = getIndexFromCoordinates(move);
            index = convertIndex(index, bottomColor);
            const square = document.getElementById(`square-${index}`);
            if (square) {
                square.classList.add('highlight');
            }
        });
    } catch (error) {
        console.error('Error getting possible moves:', error);
    }
}

function getPieceAt(coords) {
    const [row, col] = coords;
    return board[row][col] && board[row][col] !== '.' ? board[row][col] : null;
}

// Attach click event listeners to each square.
squares.forEach(square => {
square.addEventListener('click', handleSquareClick);
});

// Handler for the Restart button.
document.getElementById('restart-btn').addEventListener('click', () => {
fetch('/restart', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.bottom_color) {
            window.bottomColor = data.bottom_color;  // Update here
        }
        updateBoard();
        // Reattach click listeners if they were removed.
        squares.forEach(square => square.addEventListener('click', handleSquareClick));
    })
    .catch(error => console.error('Error restarting game:', error));
});

// Handler for the Quit button.
document.getElementById('quit-btn').addEventListener('click', () => {
fetch('/quit', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
    alert(data.message);
    // Optionally disable further moves.
    squares.forEach(square => square.removeEventListener('click', handleSquareClick));
    })
    .catch(error => console.error('Error quitting game:', error));
});

document.addEventListener('DOMContentLoaded', () => {
    const chessBoard = document.getElementById('chess-board');
    chessBoard.innerHTML = ''; // Clear any existing squares

    for (let i = 0; i < 64; i++) {
        const square = document.createElement('div');
        const row = Math.floor(i / 8);
        const col = i % 8;
        // Alternate classes based on position
        const isLight = (row + col) % 2 === 0;
        square.className = isLight ? 'square light' : 'square dark';
        square.id = `square-${i}`;
        chessBoard.appendChild(square);
    }

    squares = document.querySelectorAll('.square');
    squares.forEach(square => {
        square.addEventListener('click', handleSquareClick);
    });

    updateBoard(); // Initial board setup
});

// Initial board update when page loads.
updateBoard();
