DEVICES_GRAPHQL_QUERY = """
query devices($forceUpdate: Boolean, $junctionIds: [String]) {
    devices(forceUpdate: $forceUpdate, junctionIds: $junctionIds) {
        brand
        model
        deviceType
        dsn
        junctionId
        name
        serial
        install {
            location
        }
        data {
            __typename
            temperatureSetpoint
            temperatureSetpointPending
            temperatureSetpointPrevious
            temperatureSetpointMaximum
            modes {
                mode
                controls
            }
            isOnline
            ... on NextGenHeatPump {
                firmwareVersion
                hotWaterStatus
                mode
                modePending
            }
            ... on RE3Connected {
                firmwareVersion
                hotWaterStatus
                mode
                modePending
            }
        }
    }
}
"""

DEVICES_BASIC_INFO_GRAPHQL_QUERY = """
query devices($forceUpdate: Boolean, $junctionIds: [String]) {
    devices(forceUpdate: $forceUpdate, junctionIds: $junctionIds) {
        brand
        model
        deviceType
        dsn
        junctionId
        name
        serial
    }
}
"""

ENERGY_USE_DATA_GRAPHQL_QUERY = """
query getEnergyUseData($dsn: String!, $deviceType: DeviceType!) {
    getEnergyUseData(dsn: $dsn, deviceType: $deviceType) {
        average
        graphData {
            date
            kwh
        }
        lifetimeKwh
        startDate
    }
}
"""

ALL_DEVICE_DATA_GRAPHQL_QUERY = """
query devices($forceUpdate: Boolean, $junctionIds: [String]) {
  devices(forceUpdate: $forceUpdate, junctionIds: $junctionIds) {
    alertSettings {
      faultCode {
        major {
          email
          sms
        }
        minor {
          email
          sms
        }
      }
      operatingSetPoint {
        email
        sms
      }
      tankTemperature {
        highTemperature {
          email
          sms

          value
        }
        lowTemperature {
          email
          sms

          value
        }
      }
    }
    brand
    deviceType
    dsn
    hardware {
      hasBluetooth
      interface
    }
    id
    install {
      address
      city
      country
      date
      email
      group
      location
      phone
      postalCode
      professional
      registeredOwner
      registrationDate
      state
    }
    isRegistered
    junctionId
    lastUpdate
    model
    name
    permissions
    productId
    serial
    users {
      contactId
      email
      firstName
      isSelf
      lastName
      permissions
    }

    data {
      __typename
      activeAlerts {
        active
        code
        information {
          en {
            advancedText
            advancedTitle
            text
            title
          }
          fr {
            advancedText
            advancedTitle
            text
            title
          }
        }
        shouldRestrictChanges
        shouldShowSoftReset
        timestamp
        type
      }
      alertHistory {
        active
        code
        information {
          en {
            advancedText
            advancedTitle
            text
            title
          }
          fr {
            advancedText
            advancedTitle
            text
            title
          }
        }
        shouldRestrictChanges
        shouldShowSoftReset
        timestamp
        type
      }
      isOnline
      isWifi
      lastUpdate
      signalStrength
      heaterSsid
      ssid
      temperatureSetpoint
      temperatureSetpointPending
      temperatureSetpointPrevious
      temperatureSetpointMaximum
      error
      modes {
        mode
        controls
      }

      ... on HeatPump {
        firmwareVersion
        isAdvancedLoadUpMore
        isDemandResponsePaused
        isEnrolled
        isLeakDetectionOn
        leakDetectionStatus
        mode
        modePending
        canEditTimeOfUse
        hotWaterStatus

        timeOfUseData {
          appliedOn
          energyUsePreference
          tariffCode
          tariffID
          utility
          utilityID
        }
      }

      ... on CommercialGas {
        blockedInletPS
        blockedOutletPS
        blowerProverPS
        burnerOnTime
        ccbVersion
        ecoContact
        elapsedTime
        hasIdr
        ignitionTrials
        isExternalEnabled
        isFlameDetected
        isGasValveOn
        isIdrEnabled
        isIgniterOn
        isUseExternalEnabled
        lowGasPS
        operatingMode
        status
        temperatureActual
        temperatureDifferential
        temperatureDifferentialPending
        temperatureDifferentialPrevious
        totalCycleCount
        uimVersion
      }

      ... on RE3Connected {
        firmwareVersion
        hotWaterStatus
        isAdvancedLoadUpMore
        isCtaUcmPresent
        isDemandResponsePaused
        isEnrolled
        mode
        modePending
        vacationModeRemainingDays
        isLowes
        isAltMcu
        canEditTimeOfUse

        timeOfUseData {
          appliedOn
          energyUsePreference
          tariffCode
          tariffID
          utility
          utilityID
        }

        consumerScheduleData {
          appliedOn
          schedules {
            days
            id
            name
            times {
              time
              meridiem
            }
          }
        }
      }

      ... on NextGenHeatPump {
        firmwareVersion
        hotWaterStatus
        isAdvancedLoadUpMore
        isCtaUcmPresent
        isDemandResponsePaused
        isEnrolled
        mode
        modePending
        vacationModeRemainingDays
        electricModeRemainingDays
        isLowes
        canEditTimeOfUse

        timeOfUseData {
          appliedOn
          energyUsePreference
          tariffCode
          tariffID
          utility
          utilityID
        }

        consumerScheduleData {
          appliedOn
          schedules {
            days
            id
            name
            times {
              time
              meridiem
            }
          }
        }
      }

      ... on RE3Premium {
        firmwareVersion
        hotWaterStatus
        isAdvancedLoadUpMore
        isCtaUcmPresent
        isDemandResponsePaused
        isEnrolled
        mode
        modePending
        vacationModeRemainingDays
        guestModeRemainingDays
        canEditTimeOfUse
        hotWaterPlusLevel

        timeOfUseData {
          appliedOn
          energyUsePreference
          tariffCode
          tariffID
          utility
          utilityID
        }

        consumerScheduleData {
          appliedOn
          schedules {
            days
            id
            name
            times {
              time
              meridiem
            }
          }
        }
      }

      ... on Mustang {
        firmwareVersion
      }
    }
  }
}
"""
