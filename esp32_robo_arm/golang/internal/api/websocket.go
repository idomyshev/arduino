package api

import (
	"log"
	"net/http"
	"robot-arm-go/internal/models"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Разрешаем все origin для разработки
	},
}

func (h *Handlers) WebSocketHandler(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("WebSocket upgrade failed: %v", err)
		return
	}
	defer conn.Close()

	log.Println("WebSocket client connected")

	for {
		// Читаем как общий JSON объект
		var rawMsg map[string]interface{}
		err := conn.ReadJSON(&rawMsg)
		if err != nil {
			log.Printf("WebSocket read error: %v", err)
			break
		}

		log.Printf("Received WebSocket message: %+v", rawMsg)

		// Определяем тип команды
		var command string
		if cmd, ok := rawMsg["command"].(string); ok {
			command = cmd
			log.Printf("Found command field: '%s'", command)
		} else if msgType, ok := rawMsg["type"].(string); ok {
			command = msgType
			log.Printf("Found type field: '%s'", command)
		} else {
			log.Printf("No command or type field found in message: %+v", rawMsg)
			h.sendError(conn, "No command or type field found")
			continue
		}

		// Проверяем, что команда не пустая
		if command == "" {
			log.Printf("Empty command received in message: %+v", rawMsg)
			h.sendError(conn, "Empty command received")
			continue
		}

		// Обработка команд
		log.Printf("Processing command: '%s'", command)
		switch command {
		case "connect":
			h.handleConnectCommand(conn)
		case "disconnect":
			h.handleDisconnectCommand(conn)
		case "move_motor":
			h.handleMoveMotorCommand(conn, rawMsg)
		case "stop_motor":
			h.handleStopMotorCommand(conn, rawMsg)
		case "stop_all":
			h.handleStopAllCommand(conn)
		case "get_status":
			h.handleGetStatusCommand(conn)
		default:
			log.Printf("Unknown command received: '%s'", command)
			h.sendError(conn, "Unknown command: '"+command+"'")
		}
	}
}

func (h *Handlers) handleConnectCommand(conn *websocket.Conn) {
	device, err := h.robotController.ScanForDevice()
	if err != nil {
		h.sendError(conn, "Device not found: "+err.Error())
		return
	}

	err = h.robotController.Connect(device)
	if err != nil {
		h.sendError(conn, "Connection failed: "+err.Error())
		return
	}

	h.sendMessage(conn, "connection_status", models.ConnectionStatus{
		Connected: true,
		Message:   "Connected to robot",
	})
}

func (h *Handlers) handleDisconnectCommand(conn *websocket.Conn) {
	err := h.robotController.Disconnect()
	if err != nil {
		h.sendError(conn, "Disconnect failed: "+err.Error())
		return
	}

	h.sendMessage(conn, "connection_status", models.ConnectionStatus{
		Connected: false,
		Message:   "Disconnected from robot",
	})
}

func (h *Handlers) handleMoveMotorCommand(conn *websocket.Conn, rawMsg map[string]interface{}) {
	if !h.robotController.IsConnected() {
		h.sendError(conn, "Not connected to robot")
		return
	}

	// Извлекаем параметры из rawMsg
	motor, ok1 := rawMsg["motor"].(float64)
	direction, ok2 := rawMsg["direction"].(string)
	speed, ok3 := rawMsg["speed"].(float64)

	if !ok1 || !ok2 || !ok3 {
		h.sendError(conn, "Invalid motor command parameters")
		return
	}

	cmd := models.MotorCommand{
		Motor:     int(motor),
		Direction: direction,
		Speed:     int(speed),
	}

	err := h.robotController.SendCommand(cmd)
	if err != nil {
		h.sendError(conn, "Failed to send command: "+err.Error())
		return
	}

	h.sendMessage(conn, "motor_command", gin.H{
		"success": true,
		"message": "Motor command sent",
	})
}

func (h *Handlers) handleStopMotorCommand(conn *websocket.Conn, rawMsg map[string]interface{}) {
	if !h.robotController.IsConnected() {
		h.sendError(conn, "Not connected to robot")
		return
	}

	// Извлекаем номер мотора
	motor, ok := rawMsg["motor"].(float64)
	if !ok {
		h.sendError(conn, "Invalid motor parameter")
		return
	}

	motorCmd := models.MotorCommand{
		Motor:     int(motor),
		Direction: "stop",
		Speed:     0,
	}

	err := h.robotController.SendCommand(motorCmd)
	if err != nil {
		h.sendError(conn, "Failed to stop motor: "+err.Error())
		return
	}

	h.sendMessage(conn, "motor_command", gin.H{
		"success": true,
		"message": "Motor stopped",
	})
}

func (h *Handlers) handleStopAllCommand(conn *websocket.Conn) {
	if !h.robotController.IsConnected() {
		h.sendError(conn, "Not connected to robot")
		return
	}

	err := h.robotController.StopAllMotors()
	if err != nil {
		h.sendError(conn, "Failed to stop all motors: "+err.Error())
		return
	}

	h.sendMessage(conn, "motor_command", gin.H{
		"success": true,
		"message": "All motors stopped",
	})
}

func (h *Handlers) handleGetStatusCommand(conn *websocket.Conn) {
	h.sendMessage(conn, "status", gin.H{
		"robot_connected": h.robotController.IsConnected(),
		"active_connections": 1, // Пока упрощенно
	})
}

func (h *Handlers) sendMessage(conn *websocket.Conn, msgType string, data interface{}) {
	msg := models.WebSocketMessage{
		Type: msgType,
		Data: data,
	}

	if err := conn.WriteJSON(msg); err != nil {
		log.Printf("WebSocket write error: %v", err)
	}
}

func (h *Handlers) sendError(conn *websocket.Conn, message string) {
	msg := models.WebSocketMessage{
		Type:    "error",
		Message: message,
	}

	if err := conn.WriteJSON(msg); err != nil {
		log.Printf("WebSocket write error: %v", err)
	}
}
