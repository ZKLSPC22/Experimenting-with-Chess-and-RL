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
let botEnabled = null;
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
    console.log('Starting updateBoard function'); // Log when the function starts
    try {
        console.log('Fetching board data from /board'); // Log before fetching board data
        const response = await fetch('/board');
        console.log('Board data fetched, parsing JSON'); // Log after fetching, before parsing JSON
        const data = await response.json();
        console.log('Board data parsed:', data); // Log the parsed data
        console.log('Updating board variable'); // Log before updating the board variable
        board = data.board;
        console.log('Updating turnColor variable:', data.turn_color); // Log before updating turnColor
        turnColor = data.turn_color;
        console.log('Iterating over squares to update them'); // Log before iterating over squares
        squares.forEach((square, index) => {
            console.log('Processing square at index:', index); // Log the current square index
            index = convertIndex(index, bottomColor);
            console.log('Converted index:', index); // Log the converted index
            const [row, col] = getCoordinatesFromIndex(index);
            console.log('Coordinates for square:', { row, col }); // Log the coordinates
            const piece = board[row][col];
            console.log('Piece at coordinates:', piece); // Log the piece at the coordinates
            square.textContent = (piece && piece !== '.') 
                ? pieceIcons[piece] || piece 
                : '';
            console.log('Updated square text content:', square.textContent); // Log the updated text content
            square.style.color = piece && piece === piece.toLowerCase() 
                ? 'black' 
                : 'white';
            console.log('Updated square color:', square.style.color); // Log the updated color
        });
        console.log('Finished updating all squares'); // Log after all squares are updated
    } catch (error) {
        console.error('Error updating board:', error); // Log any errors
    }
    console.log('Finished updateBoard function'); // Log when the function ends
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
            if (botEnabled != null) {
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
                if (data.promotion_needed) {
                    // 显示升变选择对话框
                    const choice = await showPromotionDialog();
                    if (choice) {
                        // 发送升变选择
                        const promotionResponse = await fetch('/promote', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                start: start,
                                end: end,
                                piece_type: choice 
                            })
                        });
                        const promotionData = await promotionResponse.json();
                        if (promotionData.status === 'success') {
                            await updateBoard();
                            handleGameEnd(promotionData);
                        }
                    }
                } else {
                    handleGameEnd(data);
                }
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
    const botControls = document.getElementById('bot-controls');
    
    // Handle ALL checkbox changes in the container
    botControls.addEventListener('change', (e) => {
        if (!e.target.matches('input[type="checkbox"]')) return;
        
        const checkboxes = botControls.querySelectorAll('input[type="checkbox"]');
        const checkedBot = e.target.checked ? e.target.value : null;

        // Uncheck all others when a checkbox is checked
        if (e.target.checked) {
            checkboxes.forEach(checkbox => {
                if (checkbox !== e.target) checkbox.checked = false;
            });
        }
        
        // Your existing API call
        fetch('/bot-mode', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({bot_enabled: checkedBot})
        }).catch(console.error);
        console.log('setupBotToggle updateBoard');
        updateBoard();
    });
}

document.getElementById('restart-btn').addEventListener('click', async () => {
    try {
        const response = await fetch('/restart', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            // 重置所有游戏状态
            clearSquareHighlights();
            clearSquareSelection();
            selectedSquare = null;
            selectedSquareElement = null;
            
            // 重新启用所有方格的点击事件
            squares.forEach(square => {
                square.removeEventListener('click', handleSquareClick);
                square.addEventListener('click', handleSquareClick);
            });
            
            // 重置机器人状态
            const botCheckboxes = document.querySelectorAll('#bot-controls input[type="checkbox"]');
            botCheckboxes.forEach(checkbox => checkbox.checked = false);
            botEnabled = null;
            
            // 更新游戏状态
            bottomColor = data.bottom_color;
            turnColor = data.turn_color;
            board = data.board;
            
            // 更新棋盘显示
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
            
            alert(data.message);
        } else {
            throw new Error('Failed to restart game');
        }
    } catch (error) {
        console.error('Error restarting game:', error);
        alert('Failed to restart game. Please try again.');
    }
});


// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initializeChessBoard();
    setupBotToggle();
    console.log('DOM updateBoard');
    updateBoard();
});

// 添加升变选择对话框函数
async function showPromotionDialog() {
    // 创建对话框容器
    const dialog = document.createElement('div');
    dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        z-index: 1000;
    `;
    dialog.innerHTML = `
        <h3 style="margin-bottom: 15px;">选择升变棋子</h3>
        <div style="display: flex; gap: 10px;">
            <button class="promotion-btn" data-piece="Q">${pieceIcons['Q']}</button>
            <button class="promotion-btn" data-piece="R">${pieceIcons['R']}</button>
            <button class="promotion-btn" data-piece="B">${pieceIcons['B']}</button>
            <button class="promotion-btn" data-piece="N">${pieceIcons['N']}</button>
        </div>
    `;

    // 创建遮罩层
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 999;
    `;

    // 添加到文档
    document.body.appendChild(overlay);
    document.body.appendChild(dialog);

    // 设置按钮样式
    const buttons = dialog.querySelectorAll('.promotion-btn');
    buttons.forEach(btn => {
        btn.style.cssText = `
            width: 50px;
            height: 50px;
            font-size: 30px;
            border: 1px solid #ccc;
            background: white;
            cursor: pointer;
            border-radius: 4px;
        `;
    });

    // 返回Promise以等待用户选择
    return new Promise(resolve => {
        buttons.forEach(btn => {
            btn.onclick = () => {
                const piece = btn.dataset.piece;
                document.body.removeChild(overlay);
                document.body.removeChild(dialog);
                resolve(piece);
            };
        });
    });
}
