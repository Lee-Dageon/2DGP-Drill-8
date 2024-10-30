from pico2d import load_image, get_time

from state_machine import (StateMachine, time_out, space_down, right_down, left_down, left_up, right_up, start_event,
                           a_down, a_up)


class Idle:
    @staticmethod
    def enter(boy, e):
        boy.action = 3
        if right_down(e) or left_up(e):
            boy.action = 2
            boy.face_dir = -1
        elif left_down(e) or right_up(e) or start_event(e):
            boy.action = 3
            boy.face_dir = 1

        boy.dir = 0 #정지 상태이다.
        boy.frame = 0
        # 현재 시간을 저장
        boy.start_time = get_time()
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 3:
            boy.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class Sleep:
    @staticmethod
    def enter(boy, e):
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1: #오른쪽 바라보는 상태에서 눕기
            boy.image.clip_composite_draw(
                boy.frame * 100, 300, 100, 100,
                3.141592/2, # 90도 회전
                '', # 좌우상하 반전 X
                boy.x - 25, boy.y - 25, 100, 100
        )

        elif boy.face_dir == -1: #왼쪽 바라보는 상태에서 눕기
            boy.image.clip_composite_draw(
                boy.frame * 100, 200, 100, 100,
                -3.141592/2, # 90도 회전
                '', # 좌우상하 반전 X
                boy.x + 25, boy.y - 25, 100, 100
        )



class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):
            boy.dir = 1 #오른쪽 방향
            boy.action = 1

        elif left_down(e) or right_up(e):
            boy.dir = -1
            boy.action = 0

        boy.frame = 0

        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy, screen_width=800):
        # 화면의 왼쪽 끝에 도달했을 때, 왼쪽으로 더 이상 이동하지 않도록 설정
        if boy.x <= 0 and boy.dir == -1:
            boy.dir = 0  # 왼쪽으로 이동을 멈춤
        # 화면의 오른쪽 끝에 도달했을 때, 오른쪽으로 더 이상 이동하지 않도록 설정
        elif boy.x >= screen_width and boy.dir == 1:
            boy.dir = 0  # 오른쪽으로 이동을 멈춤

        # 방향에 따라 boy의 위치를 업데이트
        boy.x += boy.dir * 10
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(
            boy.frame*100, boy.action*100, 100, 100,
            boy.x, boy.y
        )
        pass


class AutoRun:
    @staticmethod
    def enter(boy, e):
        boy.dir = 1
        boy.frame = 0
        boy.action = 1
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy, screen_width=800):
        if boy.x <= 0:
            boy.dir = 1  # 오른쪽으로 전환
            boy.action = 1
        elif boy.x >= screen_width:
            boy.dir = -1  # 왼쪽으로 전환
            boy.action = 0

        boy.x += boy.dir * 30
        boy.frame = (boy.frame + 1) % 8

        if get_time() - boy.start_time > 5:
            boy.state_machine.add_event(('TIME_OUT', 0))

        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(
            boy.frame * 100, boy.action * 100, 100, 100,
            boy.x, boy.y+25, 200, 200
        )
        pass


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self) # 소년 객체의 state machine 생성
        self.state_machine.start(Idle) # 초기 상태가 Idle
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, a_down: AutoRun, a_up: AutoRun},
                Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, a_down: AutoRun, a_up:AutoRun},
                Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle},
                AutoRun: {a_down: AutoRun, right_down: Run, left_down: Run, right_up: Run, left_up: Run, a_up: AutoRun, time_out: Idle}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        # event : 입력 이벤트 key mouse
        # 우리가 state machine 전달해줄 것은 튜플 (  ,  )
        self.state_machine.add_event(
            ('INPUT',event)
        ) #내 이벤트를 쟁여놔, 튜플 형식 이벤트로 가공

    def draw(self):
        self.state_machine.draw()

