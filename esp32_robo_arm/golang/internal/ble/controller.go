package ble

import (
	"encoding/json"
	"fmt"
	"log"
	"robot-arm-go/internal/models"

	"tinygo.org/x/bluetooth"
)

const (
	SERVICE_UUID       = "12345678-1234-1234-1234-123456789abc"
	CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"
	DEVICE_NAME        = "ESP32-RobotArm"
)

type RobotController struct {
	device    *bluetooth.Device
	connected bool
	logger    *log.Logger
}

func NewRobotController() *RobotController {
	return &RobotController{
		connected: false,
		logger:    log.New(log.Writer(), "[BLE] ", log.LstdFlags),
	}
}

func (r *RobotController) ScanForDevice() (*bluetooth.Device, error) {
	r.logger.Println("Scanning for ESP32 Robot Arm...")

	// Пока что возвращаем mock устройство для тестирования
	// В реальной реализации здесь будет BLE сканирование
	r.logger.Println("Mock device found for testing")
	
	// Создаем mock устройство
	mockDevice := &bluetooth.Device{}
	return mockDevice, nil
}

func (r *RobotController) Connect(device *bluetooth.Device) error {
	r.logger.Printf("Connecting to device...")

	r.device = device
	r.connected = true
	r.logger.Printf("Connected to device")

	return nil
}

func (r *RobotController) Disconnect() error {
	if r.device != nil && r.connected {
		err := r.device.Disconnect()
		if err != nil {
			return fmt.Errorf("disconnect failed: %v", err)
		}

		r.connected = false
		r.logger.Println("Disconnected")
	}

	return nil
}

func (r *RobotController) SendCommand(cmd models.MotorCommand) error {
	if !r.connected {
		return fmt.Errorf("not connected to device")
	}

	jsonCmd, err := json.Marshal(cmd)
	if err != nil {
		return fmt.Errorf("failed to marshal command: %v", err)
	}

	r.logger.Printf("Sending command: %s", string(jsonCmd))

	// Пока что просто логируем команду, так как BLE API может отличаться
	// В реальной реализации здесь будет отправка через BLE
	r.logger.Printf("Command would be sent via BLE: %s", string(jsonCmd))

	return nil
}

func (r *RobotController) StopAllMotors() error {
	r.logger.Println("Stopping all motors...")

	for motor := 0; motor < 3; motor++ {
		cmd := models.MotorCommand{
			Motor:     motor,
			Direction: "forward",
			Speed:     0,
		}

		err := r.SendCommand(cmd)
		if err != nil {
			return fmt.Errorf("failed to stop motor %d: %v", motor, err)
		}
	}

	return nil
}

func (r *RobotController) IsConnected() bool {
	return r.connected
}

func (r *RobotController) GetDeviceInfo() string {
	if r.device != nil {
		return fmt.Sprintf("Device: %s (%s)", r.device.Address.String(), DEVICE_NAME)
	}
	return "No device connected"
}
