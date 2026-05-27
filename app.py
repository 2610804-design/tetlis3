import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="스트림릿 테트리스", page_icon="🕹️", layout="centered")

st.title("🕹️ 클래식 테트리스 게임 🧱")
st.write("웹 브라우저에서 바로 즐기는 테트리스입니다. 게임 화면을 한 번 클릭한 뒤 방향키로 조작하세요!")

# 2. HTML5 + JavaScript 테트리스 엔진 코드 (오타 수정 완료)
tetris_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            background-color: #0e1117;
            color: white;
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 10px;
        }
        #game-container {
            display: flex;
            gap: 20px;
            background: #1e222b;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            border: 1px solid #4e5561;
        }
        canvas {
            border: 2px solid #4e5561;
            background-color: #111;
        }
        #side-panel {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            width: 130px;
        }
        .info-box {
            background: #2d323f;
            padding: 15px 10px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 20px;
        }
        .score-label {
            font-size: 14px;
            color: #aaa;
            letter-spacing: 1px;
        }
        .score-val {
            font-size: 28px;
            font-weight: bold;
            color: #00ffcc;
            margin-top: 5px;
        }
        .controls {
            font-size: 12px;
            color: #ccc;
            line-height: 1.6;
            background: #252936;
            padding: 10px;
            border-radius: 5px;
        }
        .controls strong {
            color: #ff9900;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="tetris" width="240" height="400"></canvas>
        <div id="side-panel">
            <div class="info-box">
                <div class="score-label">SCORE</div>
                <div id="score" class="score-val">0</div>
            </div>
            <div class="controls">
                <strong>[조작 방법]</strong><br>
                ← : 왼쪽 이동<br>
                → : 오른쪽 이동<br>
                ↓ : 빠른 낙하<br>
                ↑ : 블록 회전<br>
                Space : 한방 낙하
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('tetris');
        const context = canvas.getContext('2d');
        context.scale(20, 20);

        function createMatrix(w, h) {
            const matrix = [];
            while (h--) { matrix.push(new Array(w).fill(0)); }
            return matrix;
        }

        function createPiece(type) {
            if (type === 'I') return [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]];
            if (type === 'L') return [[0,2,0],[0,2,0],[0,2,2]];
            if (type === 'J') return [[0,3,0],[0,3,0],[3,3,0]];
            if (type === 'O') return [[4,4],[4,4]];
            if (type === 'Z') return [[5,5,0],[0,5,5],[0,0,0]];
            if (type === 'S') return [[0,6,6],[6,6,0],[0,0,0]];
            if (type === 'T') return [[0,7,0],[7,7,7],[0,0,0]];
        }

        const colors = [null, '#FF0D72', '#0DC2FF', '#0DFF72', '#F538FF', '#FF8E0D', '#FFE138', '#3877FF'];
        const arena = createMatrix(12, 20);
        const player = { pos: {x: 0, y: 0}, matrix: null, score: 0 };

        function drawMatrix(matrix, offset) {
            matrix.forEach((row, y) => {
                row.forEach((value, x) => {
                    if (value !== 0) {
                        context.fillStyle = colors[value];
                        context.fillRect(x + offset.x, y + offset.y, 1, 1);
                        context.strokeStyle = '#1e222b';
                        context.lineWidth = 0.05;
                        context.strokeRect(x + offset.x, y + offset.y, 1, 1);
                    }
                });
            });
        }

        function draw() {
            context.fillStyle = '#111';
            context.fillRect(0, 0, canvas.width, canvas.height);
            drawMatrix(arena, {x: 0, y: 0});
            drawMatrix(player.matrix, player.pos);
        }

        function merge(arena, player) {
            player.matrix.forEach((row, y) => {
                row.forEach((value, x) => {
                    if (value !== 0) {
                        arena[y + player.pos.y][x + player.pos.x] = value;
                    }
                });
            });
        }

        function collide(arena, player) {
            const [m, o] = [player.matrix, player.pos];
            for (let y = 0; y < m.length; ++y) {
                for (let x = 0; x < m[y].length; ++x) {
                    if (m[y][x] !== 0 && (arena[y + o.y] && arena[y + o.y][x + o.x]) !== 0) {
                        return true;
                    }
                }
            }
            return false;
        }

        function arenaSweep() {
            let rowCount = 1;
            outer: for (let y = arena.length - 1; y > 0; --y) {
                for (let x = 0; x < arena[y].length; ++x) {
                    if (arena[y][x] === 0) { continue outer; }
                }
                const row = arena.splice(y, 1)[0].fill(0);
                arena.unshift(row);
                ++y;
                player.score += rowCount * 10;
                rowCount *= 2;
            }
        }

        let dropCounter = 0;
        let dropInterval = 1000;
        let lastTime = 0;

        function update(time = 0) {
            const deltaTime = time - lastTime;
            lastTime = time;
            dropCounter += deltaTime;
            if (dropCounter > dropInterval) { playerDrop(); }
            draw();
            requestAnimationFrame(update);
        }

        function playerDrop() {
            player.pos.y++;
            if (collide(arena, player)) {
                player.pos.y--;
                merge(arena, player);
                playerReset();
                arenaSweep();
                updateScore();
            }
            dropCounter = 0;
        }

        function playerMove(dir) {
            player.pos.x += dir;
            if (collide(arena, player)) { player.pos.x -= dir; }
        }

        function playerReset() {
            const pieces = 'ILJOZST'; // ◀ [수정] 기존 '0'에서 알파벳 'O'로 완벽 교체!
            player.matrix = createPiece(pieces[pieces.length * Math.random() | 0]);
            player.pos.y = 0;
            player.pos.x = (arena[0].length / 2 | 0) - (player.matrix[0].length / 2 | 0);
            if (collide(arena, player)) {
                arena.forEach(row => row.fill(0));
                player.score = 0;
                updateScore();
            }
        }

        function playerRotate(dir) {
            const pos = player.pos.x;
            let offset = 1;
            rotate(player.matrix, dir);
            while (collide(arena, player)) {
                player.pos.x += offset;
                offset = -(offset + (offset > 0 ? 1 : -1));
                if (offset > player.matrix[0].length) {
                    rotate(player.matrix, -dir);
                    player.pos.x = pos;
                    return;
                }
            }
        }

        function rotate(matrix, dir) {
            for (let y = 0; y < matrix.length; ++y) {
                for (let x = 0; x < y; ++x) {
                    [matrix[x][y], matrix[y][x]] = [matrix[y][x], matrix[x][y]];
                }
            }
            if (dir > 0) { matrix.forEach(row => row.reverse()); } 
            else { matrix.reverse(); }
        }

        function updateScore() {
            document.getElementById('score').innerText = player.score;
        }

        document.addEventListener('keydown', event => {
            if ([32, 37, 38, 39, 40].indexOf(event.keyCode) > -1) {
                event.preventDefault();
            }
            
            if (event.keyCode === 37) { playerMove(-1); } 
            else if (event.keyCode === 39) { playerMove(1); } 
            else if (event.keyCode === 40) { playerDrop(); } 
            else if (event.keyCode === 38) { playerRotate(1); }
            else if (event.keyCode === 32) {
                while (!collide(arena, player)) { player.pos.y++; }
                player.pos.y--;
                merge(arena, player);
                playerReset();
                arenaSweep();
                updateScore();
            }
        });

        playerReset();
        updateScore();
        update();
    </script>
</body>
</html>
"""

# 3. 테트리스 컴포넌트 높이 넉넉하게 지정
components.html(tetris_html, height=480)

st.divider()
st.info("💡 **플레이 방법**: 마우스로 게임 화면 내부(검은 창 쪽)를 **콕! 한 번 클릭**해 준 뒤 키보드 방향키를 누르면 블록이 움직입니다!")
