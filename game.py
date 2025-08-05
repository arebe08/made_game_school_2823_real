import streamlit as st
import time
import random

# 스트림릿 페이지 기본 설정
st.set_page_config(page_title="Falling Blocks Game", layout="wide")

# 세션 상태 초기화
if 'player_x' not in st.session_state:
    st.session_state.player_x = 250
    st.session_state.score = 0
    st.session_state.best_score = 0
    st.session_state.obstacles = []
    st.session_state.last_spawn_time = time.time()
    st.session_state.game_over = False
    st.session_state.game_start_time = time.time()

# 화면 크기
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 20
OBSTACLE_SIZE = 30
PLAYER_Y = CANVAS_HEIGHT - PLAYER_HEIGHT - 10

# 속도 증가 변수
def get_speed(elapsed_time):
    return min(8, 2 + elapsed_time / 10)

# 장애물 생성 주기 조절
def get_spawn_interval(elapsed_time):
    return max(0.3, 1.2 - elapsed_time / 30)

# 게임 초기화
def reset_game():
    st.session_state.player_x = 250
    st.session_state.score = 0
    st.session_state.obstacles = []
    st.session_state.last_spawn_time = time.time()
    st.session_state.game_over = False
    st.session_state.game_start_time = time.time()

# UI: 점수
st.sidebar.title("점수판")
st.sidebar.markdown(f"**현재 점수:** {int(st.session_state.score)}")
st.sidebar.markdown(f"**최고 점수:** {int(st.session_state.best_score)}")

# 게임 재시작 버튼
if st.session_state.game_over:
    if st.button("🔁 게임 다시 시작"):
        reset_game()

# 키 입력
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("⬅️ 왼쪽"):
        st.session_state.player_x -= 20
        if st.session_state.player_x < 0:
            st.session_state.player_x = 0
with col3:
    if st.button("➡️ 오른쪽"):
        st.session_state.player_x += 20
        if st.session_state.player_x > CANVAS_WIDTH - PLAYER_WIDTH:
            st.session_state.player_x = CANVAS_WIDTH - PLAYER_WIDTH

# 시간 기반 점수 업데이트
if not st.session_state.game_over:
    elapsed = time.time() - st.session_state.game_start_time
    st.session_state.score = elapsed * 100

# 장애물 업데이트
current_time = time.time()
if not st.session_state.game_over:
    # 장애물 생성
    if current_time - st.session_state.last_spawn_time > get_spawn_interval(elapsed):
        st.session_state.last_spawn_time = current_time
        st.session_state.obstacles.append([random.randint(0, CANVAS_WIDTH - OBSTACLE_SIZE), 0])

    # 장애물 이동
    new_obstacles = []
    for obs in st.session_state.obstacles:
        obs[1] += get_speed(elapsed) * 5
        # 충돌 판정
        if (
            PLAYER_Y < obs[1] + OBSTACLE_SIZE and
            obs[1] < PLAYER_Y + PLAYER_HEIGHT and
            st.session_state.player_x < obs[0] + OBSTACLE_SIZE and
            obs[0] < st.session_state.player_x + PLAYER_WIDTH
        ):
            st.session_state.game_over = True
            st.session_state.best_score = max(st.session_state.best_score, st.session_state.score)
            break
        if obs[1] < CANVAS_HEIGHT:
            new_obstacles.append(obs)
    st.session_state.obstacles = new_obstacles

# 캔버스에 그리기
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(5, 6))
ax.set_xlim(0, CANVAS_WIDTH)
ax.set_ylim(0, CANVAS_HEIGHT)
ax.axis('off')

# 플레이어
player_rect = patches.Rectangle(
    (st.session_state.player_x, PLAYER_Y),
    PLAYER_WIDTH, PLAYER_HEIGHT,
    linewidth=1, edgecolor='black', facecolor='blue'
)
ax.add_patch(player_rect)

# 장애물
for obs in st.session_state.obstacles:
    rect = patches.Rectangle(
        (obs[0], obs[1]),
        OBSTACLE_SIZE, OBSTACLE_SIZE,
        linewidth=1, edgecolor='black', facecolor='red'
    )
    ax.add_patch(rect)

st.pyplot(fig)
st.markdown("---")

# 게임 종료 메시지
if st.session_state.game_over:
    st.error(f"💥 게임 오버! 최종 점수: {int(st.session_state.score)}")
