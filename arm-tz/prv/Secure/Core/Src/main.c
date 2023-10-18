/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "gtzc.h"
#include "usart.h"
//#include "tim.h"
#include "gpio.h"
#include "cfa_engine.h"
#include "speculation.h"
#include "stm32l5xx_hal_flash.h"
#include "stm32l552xx.h"
#include "stm32l5xx_hal_cortex.h"
/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* Non-secure Vector table to jump to (internal Flash Bank2 here)             */
/* Caution: address must correspond to non-secure internal Flash where is     */
/*          mapped in the non-secure vector table                             */
#define VTOR_TABLE_NS_START_ADDR  0x08040000UL
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
static void NonSecure_Init(void);
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

//void SecureTogglePin(void)
//{
//  HAL_GPIO_TogglePin(LED_BLUE_GPIO_Port, LED_BLUE_Pin);
//}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* SAU/IDAU, FPU and interrupts secure/non-secure allocation setup done */
  /* in SystemInit() based on partition_stm32l552xx.h file's definitions. */
  /* USER CODE BEGIN 1 */

  //enable SecureFault_Handler, without this HardFault_Handler will be raised.
  SCB->SHCSR |= SCB_SHCSR_SECUREFAULTENA_Msk;

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  //init mpu configs
  MPU_init();

  /* GTZC initialisation */
  MX_GTZC_S_Init();

  /* USER CODE BEGIN SysInit */

  // Enable flash controller clock
  __HAL_RCC_FLASH_CLK_ENABLE();

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_LPUART1_UART_Init();
//  MX_TIM3_Init();
//  MX_TIM4_Init();
  /* USER CODE BEGIN 2 */
  FPU_Init();
  CFA_ENGINE_initialize();
  init_spec();
  //turn on secure LEDs
//  SecureTogglePin();

  /* USER CODE END 2 */

  /*************** Setup and jump to non-secure *******************************/


  NonSecure_Init();

  /* Non-secure software does not return, this code is not executed */
  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

void MPU_init(){
	// from "AN4838: Introduction to memory protection unit management on STM32 MCUs"

	MPU_Region_InitTypeDef MPU_InitStruct;
//	  uint8_t                Enable;                /*!< Specifies the status of the region.
//	                                                     This parameter can be a value of @ref CORTEX_MPU_Region_Enable                 */
//	  uint8_t                Number;                /*!< Specifies the number of the region to protect.
//	                                                     This parameter can be a value of @ref CORTEX_MPU_Region_Number                 */
//	  uint32_t               BaseAddress;           /*!< Specifies the base address of the region to protect.                           */
//	  uint32_t               LimitAddress;          /*!< Specifies the limit address of the region to protect.                          */
//	  uint8_t                AttributesIndex;       /*!< Specifies the memory attributes index.
//	                                                     This parameter can be a value of @ref CORTEX_MPU_Attributes_Number             */
//	  uint8_t                AccessPermission;      /*!< Specifies the region access permission type.
//	                                                     This parameter can be a value of @ref CORTEX_MPU_Region_Permission_Attributes  */
//	  uint8_t                DisableExec;           /*!< Specifies the instruction access status.
//	                                                     This parameter can be a value of @ref CORTEX_MPU_Instruction_Access            */
//	  uint8_t                IsShareable;           /*!< Specifies the shareability status of the protected region.
//	                                                     This parameter can be a value of @ref CORTEX_MPU_Access_Shareable              */

	/* Disable MPU */
	HAL_MPU_Disable();

	/* Configure NS-RAM region as Region N°0 as R/W region */
	MPU_InitStruct.Enable = MPU_REGION_ENABLE;
	MPU_InitStruct.BaseAddress = 0x20000000;
	MPU_InitStruct.LimitAddress = 0x20040000;
	MPU_InitStruct.AccessPermission = MPU_REGION_ALL_RW;
	MPU_InitStruct.Number = MPU_REGION_NUMBER0;
	MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
	HAL_MPU_ConfigRegion(&MPU_InitStruct);

	/* Configure NS-FLASH region as REGION N°1 as R/X region */
	MPU_InitStruct.BaseAddress = 0x08000000;
	MPU_InitStruct.LimitAddress = 0x08080000;
	MPU_InitStruct.AccessPermission = MPU_REGION_ALL_RO;
	MPU_InitStruct.Number = MPU_REGION_NUMBER1;
	MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_ENABLE;
	HAL_MPU_ConfigRegion(&MPU_InitStruct);

	/* Enable MPU */
	HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}

void FPU_Init(void) {
    // FPU access is controlled by the CPACR register
    // The CPACR is an ARMv8-M system control register (SCTLR)

    // Access the SCTLR register
    volatile uint32_t* cpacr = (volatile uint32_t*)0xE000ED88;

    // Enable full access to the FPU for both secure and non-secure worlds
    *cpacr |= (0xF << 20);  // Set bits 20-23 to 1111 to enable full FPU access

    // DSB (Data Synchronization Barrier) to ensure the register write completes
    __asm volatile ("dsb");

    // ISB (Instruction Synchronization Barrier) to flush the pipeline
    __asm volatile ("isb");
}

/**
  * @brief  Non-secure call function
  *         This function is responsible for Non-secure initialization and switch
  *         to non-secure state
  * @retval None
  */
static void NonSecure_Init(void)
{
  funcptr_NS NonSecure_ResetHandler;

  SCB_NS->VTOR = VTOR_TABLE_NS_START_ADDR;

  /* Set non-secure main stack (MSP_NS) */
  __TZ_set_MSP_NS((*(uint32_t *)VTOR_TABLE_NS_START_ADDR));

  /* Get non-secure reset handler */
  NonSecure_ResetHandler = (funcptr_NS)(*((uint32_t *)((VTOR_TABLE_NS_START_ADDR) + 4U)));

  /* Start non-secure state software application */
  NonSecure_ResetHandler();
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE0) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 4;
  RCC_OscInitStruct.PLL.PLLN = 55;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV7;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
