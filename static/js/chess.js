// Constants and Configurations
const pieceIcons = {
    'P': '♙', 'p': '♟',
    'R': '♖', 'r': '♜',
    'N': '♘', 'n': '♞',
    'B': '♗', 'b': '♝',
    'Q': '♕', 'q': '♛',
    'K': '♔', 'k': '♚'
};


// Game State Variables
let board = [];
let selectedSquare = null;
let selectedSquareElement = null;
let squares = [];
let botEnabled = false;
const botColor = bottomColor


// Coordinate Conversion Helpers, backend coordinates aligns with white pieces
function convertIndex(index, color) {
    return color === 'white' ? index : 63 - index;
}

function getCoordinatesFromIndex(index) {
    const row = Math.floor(index / 8);
    const col = index % 8;
    return [row, col];
}

function getIndexFromCoordinates(coords) {
    const [row, col] = coords;
    return row * 8 + col;
}


// Board Management
async function updateBoard() {
    try {
        const response = await fetch('/board');
        const data = await response.json();
        board = data.board;
        turnColor = data.turn_color;
        squares.forEach((square, index) => {
            index = convertIndex(index, bottomColor);
            const [row, col] = getCoordinatesFromIndex(index);
            const piece = board[row][col];
            
            square.textContent = (piece && piece !== '.') 
                ? pieceIcons[piece] || piece 
                : '';
            square.style.color = piece && piece === piece.toLowerCase() 
                ? 'black' 
                : 'white';
        });
    } catch (error) {
        console.error('Error updating board:', error);
    }
}

function initializeChessBoard() {
    const chessBoard = document.getElementById('chess-board');
    chessBoard.innerHTML = '';
    
    for (let i = 0; i < 64; i++) {
        const square = document.createElement('div');
        const isLight = (Math.floor(i / 8) + (i % 8)) % 2 === 0;
        square.className = `square ${isLight ? 'light' : 'dark'}`;
        square.id = `square-${i}`;
        chessBoard.appendChild(square);
    }

    squares = document.querySelectorAll('.square');
    squares.forEach(square => {
        square.addEventListener('click', handleSquareClick);
    });
}


// Game Logic
function getPieceAt(coords) {
    const [row, col] = coords;
    return board[row][col] && board[row][col] !== '.' ? board[row][col] : null;
}

function handleGameEnd(response) {
    if (response.game_over) {
        alert(response.message);
        squares.forEach(square => square.removeEventListener('click', handleSquareClick));
    }
}


// Move Handling & Visualization
async function highlightValidMoves(start) {
    try {
        const response = await fetch('/get_possible_moves', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start: start })
        });
        const data = await response.json();
        console.log("Possible moves returned:", data.moves);
        data.moves.forEach(move => {
            let index = getIndexFromCoordinates(move);
            index = convertIndex(index, bottomColor);
            document.getElementById(`square-${index}`)?.classList.add('highlight');
        });
    } catch (error) {
        console.error('Error getting possible moves:', error);
    }
}

function clearSquareHighlights() {
    squares.forEach(square => {
        if (square !== selectedSquareElement) square.style.border = '';
        square.classList.remove('highlight');
    });
}

async function handleSquareClick(event) {
    let squareIndex = Array.from(squares).indexOf(event.target);
    if (squareIndex === -1) return;

    squareIndex = convertIndex(squareIndex, bottomColor);
    const coords = getCoordinatesFromIndex(squareIndex);

    if (!selectedSquare) {
        const piece = getPieceAt(coords);
        if (piece) {
            if (turnColor === 'white' && piece !== piece.toUpperCase()) return;
            if (turnColor === 'black' && piece !== piece.toLowerCase()) return;
            if (botEnabled) {
                if (bottomColor === 'white' && piece === piece.toLowerCase()) return;
                if (bottomColor === 'black' && piece === piece.toUpperCase()) return;
            }
            clearSquareHighlights();
            selectedSquare = coords;
            selectedSquareElement = event.target;
            event.target.style.border = '2px solid red';
            await highlightValidMoves(coords);
        }
    } else {
        const [start, end] = [selectedSquare, coords];
        clearSquareHighlights();
        selectedSquareElement.style.border = '';
        selectedSquare = null;
        selectedSquareElement = null;

        try {
            const response = await fetch('/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start, end })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                await updateBoard();
                handleGameEnd(data);
            } else {
                alert('Invalid move!');
                await updateBoard();
            }
        } catch (error) {
            console.error('Move error:', error);
            await updateBoard();
        }
    }
}

function clearSquareSelection() {
    if (selectedSquareElement) {
        selectedSquareElement.style.border = '';
    }
    selectedSquare = null;
    selectedSquareElement = null;
}


// UI Controls & Event Handlers
function setupBotToggle() {
    document.getElementById('bot-toggle').addEventListener('change', function() {
        botEnabled = this.checked;
        fetch('/bot-mode', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({bot_enabled: this.checked})
        }).catch(console.error);
        updateBoard();
    });
}

document.getElementById('restart-btn').addEventListener('click', () => {
    fetch('/restart', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            clearSquareHighlights();
            clearSquareSelection();
            const botToggleElem = document.getElementById('bot-toggle');
            botToggleElem.checked = false;
            botEnabled = false;
            bottomColor = data.bottom_color;
            updateBoard();
        })
        .catch(error => console.error('Error restarting game:', error));
});


// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initializeChessBoard();
    setupBotToggle();
    updateBoard();
});
