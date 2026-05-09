# Tri-Edge Rescue

클라우드 없는 온디바이스 멀티로봇 탐색·구조 AI 프로젝트

## 1. Project Overview

**Tri-Edge Rescue**는 재난·실험실 사고 환경을 가정한 온디바이스 멀티로봇 탐색·구조 AI 시스템이다.

본 프로젝트는 두 대의 로봇이 각자 현장에서 로컬 정보를 수집하고, 원본 영상이나 대용량 센서 데이터를 중앙으로 보내지 않고, 의미 정보(summary JSON)만 Commander C에 전달하는 구조를 구현한다.

Commander C는 Robot A/B의 summary를 통합해 위험도와 상황을 판단하고, 각 로봇에게 task command를 다시 전송한다.

핵심 슬로건:

> 영상을 보내지 않고, 의미를 보낸다.

---

## 2. Core Concept

기존 클라우드 기반 구조에서는 로봇의 카메라 영상이나 센서 데이터를 외부 서버로 전송해야 하므로 다음 문제가 발생할 수 있다.

- 네트워크 불안정 시 미션 중단
- 원본 영상 전송에 따른 민감정보 노출
- 다중 로봇 환경에서 높은 통신량
- 서버 왕복 지연으로 인한 느린 대응

Tri-Edge Rescue는 각 로봇이 로컬에서 의미 정보를 생성하고, 중앙 Commander는 이 summary만 받아 판단한다.

```text
Raw Image / Sensor Stream ❌
Semantic Summary JSON ✅
