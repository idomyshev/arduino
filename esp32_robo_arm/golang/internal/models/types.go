package models

// MotorCommand - команда для мотора
type MotorCommand struct {
	Motor     int    `json:"motor"`
	Direction string `json:"direction"`
	Speed     int    `json:"speed"`
	Duration  *int   `json:"duration,omitempty"`
}

// WebSocketMessage - сообщение WebSocket
type WebSocketMessage struct {
	Type    string      `json:"type"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
}

// ConnectionStatus - статус подключения
type ConnectionStatus struct {
	Connected bool   `json:"connected"`
	Message   string `json:"message,omitempty"`
}

// MotorStatus - статус мотора
type MotorStatus struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	Position int    `json:"position"`
	Speed    int    `json:"speed"`
	IsMoving bool   `json:"isMoving"`
}

// ServerStatus - статус сервера
type ServerStatus struct {
	Status        string `json:"status"`
	Version       string `json:"version"`
	RobotConnected bool  `json:"robot_connected"`
	Timestamp     string `json:"timestamp,omitempty"`
}

// APIResponse - стандартный ответ API
type APIResponse struct {
	Status  string      `json:"status"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}
