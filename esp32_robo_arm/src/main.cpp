// ESP32 Robot Arm — три сервопривода, ESP32 core 3.x API

#include <Arduino.h>

#define M1_PWM 18 // PWM выход на PWMA (базовый поворот)
#define M1_IN1 16 // AIN1
#define M1_IN2 17 // AIN2

#define M2_PWM 19 // PWM выход на PWMB (подъем/опускание)
#define M2_IN1 21 // BIN1
#define M2_IN2 22 // BIN2

#define M3_PWM 23 // PWM выход на PWMC (сгибание/разгибание)
#define M3_IN1 25 // CIN1
#define M3_IN2 26 // CIN2

#define STBY 27 // STBY (держать HIGH)

#define PWM_FREQ 20000 // 20 кГц — плавная работа сервоприводов
#define PWM_BITS 8     // 0..255 диапазон duty

// Параметры ШИМ для плавного изменения скорости
const int MAX_PWM = 255;
const int MIN_PWM = 30; // Минимальная скорость для сервоприводов
const int STEP = 5;     // Меньший шаг для плавности

// Состояние
int speedPWM = MIN_PWM; // начальная скорость
int ds = STEP;          // направление изменения скорости (+5 / -5)
bool forward = true;    // направление вращения моторов

void setup()
{
    pinMode(M1_IN1, OUTPUT);
    pinMode(M1_IN2, OUTPUT);

    pinMode(M2_IN1, OUTPUT);
    pinMode(M2_IN2, OUTPUT);

    pinMode(M3_IN1, OUTPUT);
    pinMode(M3_IN2, OUTPUT);

    pinMode(STBY, OUTPUT);

    digitalWrite(STBY, HIGH); // включаем драйвер

    // Настройка PWM каналов для ESP32 Arduino framework 3.x
    ledcSetup(0, PWM_FREQ, PWM_BITS); // канал 0 для M1
    ledcSetup(1, PWM_FREQ, PWM_BITS); // канал 1 для M2
    ledcSetup(2, PWM_FREQ, PWM_BITS); // канал 2 для M3

    ledcAttachPin(M1_PWM, 0); // привязываем пин к каналу
    ledcAttachPin(M2_PWM, 1);
    ledcAttachPin(M3_PWM, 2);
}

void loop()
{
    // 1) применяем текущую скорость ко всем трем сервоприводам
    ledcWrite(0, speedPWM); // канал 0 для M1 (базовый поворот)
    ledcWrite(1, speedPWM); // канал 1 для M2 (подъем/опускание)
    ledcWrite(2, speedPWM); // канал 2 для M3 (сгибание/разгибание)

    // 2) устанавливаем направление вращения в зависимости от переменной forward
    if (forward)
    {
        // Вращение в одну сторону
        digitalWrite(M1_IN1, HIGH);
        digitalWrite(M1_IN2, LOW);

        digitalWrite(M2_IN1, HIGH);
        digitalWrite(M2_IN2, LOW);

        digitalWrite(M3_IN1, HIGH);
        digitalWrite(M3_IN2, LOW);
    }
    else
    {
        // Вращение в противоположную сторону
        digitalWrite(M1_IN1, LOW);
        digitalWrite(M1_IN2, HIGH);

        digitalWrite(M2_IN1, LOW);
        digitalWrite(M2_IN2, HIGH);

        digitalWrite(M3_IN1, LOW);
        digitalWrite(M3_IN2, HIGH);
    }

    delay(100); // Короткая задержка для плавности

    // 3) обновляем скорость с плавным изменением от 30 до 255 и обратно
    int next = speedPWM + ds;

    if (next > MAX_PWM)
    {
        speedPWM = MAX_PWM; // точно попадаем в 255
        ds = -STEP;         // дальше убываем
        forward = !forward;
    }
    else if (next < MIN_PWM)
    {
        speedPWM = MIN_PWM; // точно попадаем в 30
        ds = STEP;          // дальше растём
        forward = !forward; // меняем направление при достижении минимальной скорости
    }
    else
    {
        speedPWM = next; // обычный шаг
    }
}
