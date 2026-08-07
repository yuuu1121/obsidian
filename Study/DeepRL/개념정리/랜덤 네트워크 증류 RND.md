---
title: "개념정리 — 랜덤 네트워크 증류 (Random Network Distillation, RND)"
tags: [개념정리, DeepRL, 강화학습, 탐험]
related: [[Chapter 18 - 고급 탐험 기법]]
---

# 랜덤 네트워크 증류 (Random Network Distillation, RND)

> [!abstract] 한 줄 요약
> 학습되지 않는 "랜덤 고정 신경망"과 그것을 흉내 내도록 학습되는 "예측 신경망"을 나란히 두고, 예측이 잘 맞을수록(즉 그 상태에 익숙할수록) 내재적 보상을 작게, 예측이 틀릴수록(낯선 상태일수록) 내재적 보상을 크게 주는 탐험 기법이다.

## 1. 아이디어 — "낯설면 예측이 틀린다"

[[내재적 보상과 카운트 기반 탐험]]에서는 방문 횟수를 직접 세었다. 랜덤 네트워크 증류(RND)는 전혀 다른 방식으로 "낯섦"을 측정한다: **예측 오차**를 이용한다.

> [!tip] 비유 — 손글씨 따라 그리기
> 친구가 아무렇게나 그린 낙서(랜덤 신경망의 출력)를 여러분이 계속 따라 그려서 익힌다고 하자. 자주 보는 패턴의 낙서는 금방 똑같이 따라 그릴 수 있게 되지만(예측 오차 작음), 한 번도 본 적 없는 이상한 모양의 낙서가 나오면 잘 따라 그리지 못한다(예측 오차 큼). 이 "얼마나 못 따라 그렸는가"가 곧 "이 상태가 얼마나 낯선가"의 척도가 된다.

## 2. 구조 — 신경망 두 개

1. **참조 신경망(reference network, ref_net)**: 무작위로 초기화된 뒤 **절대 학습시키지 않는다.** 그냥 고정된 "임의의 답안지" 역할.
2. **학습 신경망(trained network, trn_net)**: 참조 신경망의 출력을 최대한 똑같이 흉내 내도록 **MSE(평균제곱오차) 손실로 학습**된다.

두 신경망 모두 입력은 같은 관측값(observation)이고, 출력은 숫자 하나다. "증류(distillation)"라는 이름은 큰 지식(참조망의 행동)을 작은 모델(학습망)에 옮겨 담는다는 딥러닝 용어에서 따왔다.

**내재적 보상** = 두 신경망 출력의 절댓값 차이:

$$r_i = |f_{\text{ref}}(s) - f_{\text{trn}}(s)|$$

이 상태를 많이 볼수록 학습망이 참조망을 잘 흉내 내게 되어 차이(=보상)가 작아진다. 즉 **"많이 본 상태 = 예측이 정확함 = 보너스 작음"**, **"낯선 상태 = 예측이 부정확 = 보너스 큼"** 구조다.

## 3. 코드로 보는 감 — MountainCarNetDistillery

```python
class MountainCarNetDistillery(nn.Module):
    def __init__(self, obs_size: int, hid_size: int = 128):
        super().__init__()
        # 참조망: 3개 레이어. 무작위 초기화 후 절대 학습 안 시킴
        self.ref_net = nn.Sequential(
            nn.Linear(obs_size, hid_size),
            nn.ReLU(),
            nn.Linear(hid_size, hid_size),
            nn.ReLU(),
            nn.Linear(hid_size, 1),
        )
        self.ref_net.train(False)   # 학습 모드 끄기 — 이 망은 절대 안 바뀐다
        # 학습망: 딱 1개 레이어만 — 일부러 얕게 만들어 과적합을 막는다
        self.trn_net = nn.Sequential(
            nn.Linear(obs_size, 1),
        )

    def forward(self, x):
        return self.ref_net(x), self.trn_net(x)   # 두 망의 출력을 함께 반환

    def extra_reward(self, obs):
        r1, r2 = self.forward(torch.FloatTensor([obs]))
        return (r1 - r2).abs().detach().numpy()[0][0]   # 절댓값 차이 = 내재적 보상

    def loss(self, obs_t):
        r1_t, r2_t = self.forward(obs_t)
        return F.mse_loss(r2_t, r1_t).mean()   # 학습망이 참조망을 따라가도록 학습
```

`ref_net`은 3개 레이어로 깊게, `trn_net`은 1개 레이어로 얕게 만든 이유는 **과적합 방지**다. 학습망이 너무 강력하면 관측 공간이 좁은 MountainCar 같은 문제에서는 금방 모든 상태를 다 외워버려서, 낯선 상태와 익숙한 상태를 구분하는 능력(=탐험 신호)이 사라지기 때문이다.

`extra_reward`는 두 망의 출력 차이를 계산해 내재적 보상을 만들고, `loss`는 학습망이 참조망의 출력을 흉내 내도록 MSE로 학습시키는 손실 함수다.

> [!note] 왜 이 방법이 잘 통할까?
> 참조망은 완전히 무작위라서 의미 있는 값을 내진 않지만, **같은 입력에는 항상 같은 출력**을 낸다는 성질만으로 충분하다. 학습망은 "자주 보는 입력 → 어떤 출력이 나오는지"를 점점 정확히 익히게 되고, 그 학습 진행도가 곧 "얼마나 이 상태에 익숙해졌는가"를 대변한다. 별도의 라벨이나 사람이 정한 규칙 없이, 순수하게 **예측 오차만으로 새로움을 측정**하는 것이 이 방법의 핵심이다.

## 세 줄 정리
- 학습 안 되는 무작위 신경망(ref_net)과 그걸 따라 배우는 신경망(trn_net)을 나란히 둔다.
- 두 신경망 출력의 차이(예측 오차)가 클수록 낯선 상태이므로, 그 차이를 내재적 보상으로 사용한다.
- Montezuma's Revenge 같은 극도로 보상이 희소한 Atari 게임에서 최고 수준(state-of-the-art) 성능을 보인 방법이다.
