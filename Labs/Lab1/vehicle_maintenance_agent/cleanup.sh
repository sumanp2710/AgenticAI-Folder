#!/bin/bash
set -e
# This script cleans up the agent environment by removing the agent and its associated resources.
orchestrate tools remove --name get_nearest_service_center
orchestrate tools remove --name get_vehicle_telematics

orchestrate knowledge-bases remove --name vehicle_user_manual
# orchestrate agents remove --name news_agent --kind external

orchestrate agents remove --name vehicle_telematics_agent --kind native
orchestrate agents remove --name vehicle_troubleshoot_agent --kind native

orchestrate agents list
orchestrate knowledge-bases list
orchestrate tools list