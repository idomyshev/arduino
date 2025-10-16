package api

import (
	"net/http"
	"robot-arm-go/internal/ble"
	"robot-arm-go/internal/models"
	"time"

	"github.com/gin-gonic/gin"
)

type Handlers struct {
	robotController *ble.RobotController
}

func NewHandlers(robotController *ble.RobotController) *Handlers {
	return &Handlers{
		robotController: robotController,
	}
}

func (h *Handlers) GetStatus(c *gin.Context) {
	status := models.ServerStatus{
		Status:        "running",
		Version:       "1.0.0",
		RobotConnected: h.robotController.IsConnected(),
		Timestamp:     time.Now().Format(time.RFC3339),
	}

	c.JSON(http.StatusOK, status)
}

func (h *Handlers) ConnectRobot(c *gin.Context) {
	device, err := h.robotController.ScanForDevice()
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.APIResponse{
			Status: "error",
			Error:  err.Error(),
		})
		return
	}

	err = h.robotController.Connect(device)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.APIResponse{
			Status: "error",
			Error:  err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, models.APIResponse{
		Status:  "success",
		Message: "Connected to robot",
	})
}

func (h *Handlers) DisconnectRobot(c *gin.Context) {
	err := h.robotController.Disconnect()
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.APIResponse{
			Status: "error",
			Error:  err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, models.APIResponse{
		Status:  "success",
		Message: "Disconnected from robot",
	})
}

func (h *Handlers) MoveMotor(c *gin.Context) {
	var cmd models.MotorCommand
	if err := c.ShouldBindJSON(&cmd); err != nil {
		c.JSON(http.StatusBadRequest, models.APIResponse{
			Status: "error",
			Error:  err.Error(),
		})
		return
	}

	err := h.robotController.SendCommand(cmd)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.APIResponse{
			Status: "error",
			Error:  err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, models.APIResponse{
		Status:  "success",
		Message: "Motor command sent",
	})
}

func (h *Handlers) StopAllMotors(c *gin.Context) {
	err := h.robotController.StopAllMotors()
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.APIResponse{
			Status: "error",
			Error:  err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, models.APIResponse{
		Status:  "success",
		Message: "All motors stopped",
	})
}

func (h *Handlers) GetRobotInfo(c *gin.Context) {
	info := gin.H{
		"connected": h.robotController.IsConnected(),
		"device_info": h.robotController.GetDeviceInfo(),
	}

	c.JSON(http.StatusOK, models.APIResponse{
		Status: "success",
		Data:   info,
	})
}
