# Generative Model

## 개요
Generative Model(생성 모델)은 데이터의 분포 $P(X)$ 또는 조건부 분포 $P(X|Y)$를 학습하여 새로운 데이터를 생성할 수 있는 모델이다.

## Generative vs Discriminative

| 특성 | Generative | Discriminative |
|------|------------|----------------|
| 학습 대상 | $P(X, Y)$ 또는 $P(X)$ | $P(Y|X)$ |
| 목적 | 데이터 생성 | 분류/예측 |
| 예시 | VAE, GAN | SVM, Logistic Regression |

## 종류

### 1. Explicit Density Models

#### Autoregressive Models
$$P(x) = \prod_{i=1}^{n} P(x_i | x_1, ..., x_{i-1})$$
- PixelCNN, WaveNet, GPT

#### Variational Autoencoders (VAE)
잠재 변수 $z$를 통해 데이터 생성
$$P(x) = \int P(x|z)P(z)dz$$

#### Normalizing Flows
가역 변환을 통한 밀도 추정

### 2. Implicit Density Models

#### Generative Adversarial Networks (GAN)
Generator와 Discriminator의 적대적 학습
$$\min_G \max_D V(D,G) = \mathbb{E}_{x \sim p_{data}}[\log D(x)] + \mathbb{E}_{z \sim p_z}[\log(1-D(G(z)))]$$

### 3. Diffusion Models
노이즈 추가/제거 과정을 학습
- DDPM, Stable Diffusion

## VAE 구조

```
Input → Encoder → μ, σ → z (sampling) → Decoder → Output
                    ↓
            KL Divergence Loss
```

Loss: $L = \text{Reconstruction Loss} + \text{KL Divergence}$

## GAN 구조

```
z (noise) → Generator → Fake Data ↘
                                    Discriminator → Real/Fake
            Real Data →           ↗
```

## 응용 분야
- 이미지 생성 (DALL-E, Midjourney)
- 텍스트 생성 (GPT)
- 음성 합성 (WaveNet)
- 데이터 증강

## 관련 개념
- [[Variational Inference]]
- [[Latent Variable]]
- [[Maximum Likelihood Estimation]]
