import streamlit as st
import time
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 스트림릿 기본 설정
st.set_page_config(page_title="Falling Blocks Game", layout="wide")

# 화면 설정
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 20
OBSTACLE_SIZE = 30
PLAYER_Y = 10  # 바닥에 고정

# 세션 상태 초기화
if "player_x" not in st.session_state:
    st.session_state.player_x = CANVAS_WIDTH // 2
    st.session_state.score = 0
    st.session_state.best_score = 0
    st.session_state.obstacles = []
    st.session_state.game_over = False
    st.session_state.start_time = time.time()
    st.session_state.last_spawn_time = time.time()

# 게임 재시작
def reset_game():
    st.session_state.player_x = CANVAS_WIDTH // 2
    st.session_state.score = 0
    st.session_state.obstacles = []
    st.session_state.game_over = False
    st.session_state.start_time = time.time()
    st.session_state.last_spawn_time = time.time()

# 버튼으로 캐릭터 이동
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("⬅️ 왼쪽"):
        st.session_state.player_x = max(0, st.session_state.player_x - 30)
with col3:
    if st.button("➡️ 오른쪽"):
        st.session_state.player_x = min(CANVAS_WIDTH - PLAYER_WIDTH, st.session_state.player_x + 30)

# 점수 표시
st.sidebar.title("점수판")
st.sidebar.write(f"현재 점수: **{int(st.session_state.score)}**")
st.sidebar.write(f"최고 점수: **{int(st.session_state.best_score)}**")

# 게임 오버 후 재시작 버튼
if st.session_state.game_over:
    if st.button("🔁 게임 다시 시작"):
        reset_game()

# 게임 진행 화면
placeholder = st.empty()

# 장애물 생성 주기, 속도 계산
def get_spawn_interval(elapsed_time):
    return max(0.3, 1.2 - elapsed_time / 30)

def get_speed(elapsed_time):
    # 위에서 바닥까지 1초 내 도달하도록
    return CANVAS_HEIGHT / 100

# 장애물 추가
def spawn_obstacle():
    st.session_state.obstacles.append({
        "x": random.randint(0, CANVAS_WIDTH - OBSTACLE_SIZE),
        "y": CANVAS_HEIGHT,
        "spawn_time": time.time()
    })

# 메인 루프 (Streamlit 반복 갱신)
while not st.session_state.game_over:
    elapsed = time.time() - st.session_state.start_time
    st.session_state.score = elapsed * 100

    # 장애물 생성 타이밍
    if time.time() - st.session_state.last_spawn_time > get_spawn_interval(elapsed):
        spawn_obstacle()
        st.session_state.last_spawn_time = time.time()

    # 장애물 위치 업데이트
    speed = get_speed(elapsed)
    new_obstacles = []
    for obs in st.session_state.obstacles:
        fall_time = time.time() - obs["spawn_time"]
        obs["y"] = CANVAS_HEIGHT - fall_time * speed * 100

        # 충돌 판정
        if (
            PLAYER_Y < obs["y"] + OBSTACLE_SIZE and
            obs["y"] < PLAYER_Y + PLAYER_HEIGHT and
            st.session_state.player_x < obs["x"] + OBSTACLE_SIZE and
            obs["x"] < st.session_state.player_x + PLAYER_WIDTH
        ):
            st.session_state.game_over = True
            st.session_state.best_score = max(st.session_state.best_score, st.session_state.score)
            break

        if obs["y"] > -OBSTACLE_SIZE:
            new_obstacles.append(obs)

    st.session_state.obstacles = new_obstacles

    # 그림 그리기
    fig, ax = plt.subplots(figsize=(5, 6))
    ax.set_xlim(0, CANVAS_WIDTH)
    ax.set_ylim(0, CANVAS_HEIGHT)
    ax.axis("off")

    # 캐릭터
    player_rect = patches.Rectangle(
        (st.session_state.player_x, PLAYER_Y),
        PLAYER_WIDTH, PLAYER_HEIGHT,
        linewidth=1, edgecolor='black', facecolor='blue'
    )
    ax.add_patch(player_rect)

    # 장애물
    for obs in st.session_state.obstacles:
        rect = patches.Rectangle(
            (obs["x"], obs["y"]),
            OBSTACLE_SIZE, OBSTACLE_SIZE,
            linewidth=1, edgecolor='black', facecolor='red'
        )
        ax.add_patch(rect)

    placeholder.pyplot(fig)

    # 짧은 시간 대기 후 반복
    time.sleep(0.03)
