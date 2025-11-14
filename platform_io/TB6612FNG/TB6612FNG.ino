// TB6612FNG — один мотор (канал A), ESP32 core 3.x API

#include <Arduino.h>

#define M1_PWM 18 // PWM выход на PWMA
#define M1_IN1 16 // AIN1
#define M1_IN2 17 // AIN2

#define M2_PWM 19 // PWM выход на PWMB
#define M2_IN1 21 // BIN1
#define M2_IN2 22 // BIN2

#define M3_PWM 23
#define M3_IN1 25
#define M3_IN2 26

#define STBY 27 // STBY (держать HIGH)

#define PWM_FREQ 20000 // 20 кГц — тихо для уха
#define PWM_BITS 8     // 0..255 диапазон duty

// Параметры ШИМ (для ESP32 с 8-битным ledc: 0..255)
const int MAX_PWM = 255;
const int MIN_PWM = 0;
const int STEP = 20;

// Состояние
int speedPWM = 255;  // начальная скорость
int ds = -STEP;      // направление изменения скорости (-20 / +20)
bool forward = true; // направление вращения, меняем каждый loop

void setup()
{
  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);

  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);

  pinMode(M3_IN1, OUTPUT);
  pinMode(M3_IN2, OUTPUT);

  pinMode(STBY, OUTPUT);

  digitalWrite(STBY, HIGH);               // включаем драйвер
  ledcAttach(M1_PWM, PWM_FREQ, PWM_BITS); // привязываем PWM к пину
  ledcAttach(M2_PWM, PWM_FREQ, PWM_BITS);
  ledcAttach(M3_PWM, PWM_FREQ, PWM_BITS);
}

void loop()
{
  // 1) применяем текущую скорость
  ledcWrite(M1_PWM, speedPWM);
  ledcWrite(M2_PWM, speedPWM);
  ledcWrite(M3_PWM, speedPWM);

  // 2) ставим направление (меняется на каждой итерации)
  if (forward)
  {
    digitalWrite(M1_IN1, HIGH);
    digitalWrite(M1_IN2, LOW);

    digitalWrite(M2_IN1, LOW);
    digitalWrite(M2_IN2, HIGH);

    digitalWrite(M3_IN1, LOW);
    digitalWrite(M3_IN2, HIGH);
  }
  else
  {
    digitalWrite(M1_IN1, LOW);
    digitalWrite(M1_IN2, HIGH);

    digitalWrite(M2_IN1, HIGH);
    digitalWrite(M2_IN2, LOW);

    digitalWrite(M3_IN1, LOW);
    digitalWrite(M3_IN2, HIGH);
  }

  delay(2000);

  // 3) обновляем скорость с «зажимом» на границах и сменой знака при перелёте
  int next = speedPWM + ds;

  if (next > MAX_PWM)
  {
    speedPWM = MAX_PWM; // точно попадаем в 255
    ds = -STEP;         // дальше убываем
  }
  else if (next < MIN_PWM)
  {
    speedPWM = MIN_PWM; // точно попадаем в 0
    ds = STEP;          // дальше растём
  }
  else
  {
    speedPWM = next; // обычный шаг
  }

  // 4) меняем направление каждый цикл
  forward = !forward;
}