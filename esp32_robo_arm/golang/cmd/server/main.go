package main

import (
	"log"
	"robot-arm-go/internal/api"
	"robot-arm-go/internal/ble"

	"github.com/gin-gonic/gin"
)

func main() {
	log.Println("Starting Robot Arm Go Server...")

	// Создаем контроллер робота
	robotController := ble.NewRobotController()

	// Создаем handlers
	handlers := api.NewHandlers(robotController)

	// Настраиваем Gin
	r := gin.Default()

	// CORS middleware
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// API routes
	apiGroup := r.Group("/api")
	{
		apiGroup.GET("/status", handlers.GetStatus)
		apiGroup.POST("/connect", handlers.ConnectRobot)
		apiGroup.POST("/disconnect", handlers.DisconnectRobot)
		apiGroup.POST("/motor", handlers.MoveMotor)
		apiGroup.POST("/stop-all", handlers.StopAllMotors)
		apiGroup.GET("/robot-info", handlers.GetRobotInfo)
	}

	// WebSocket
	r.GET("/ws", handlers.WebSocketHandler)

	// Статические файлы для React (если нужно)
	r.Static("/static", "../robot-web-interface/dist")
	r.GET("/", func(c *gin.Context) {
		c.File("../robot-web-interface/dist/index.html")
	})

	log.Println("Server starting on :8000")
	log.Println("WebSocket available at: ws://localhost:8000/ws")
	log.Println("API available at: http://localhost:8000/api")
	log.Println("React app available at: http://localhost:8000/")

	r.Run(":8000")
}
