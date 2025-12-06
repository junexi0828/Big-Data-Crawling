# PICU Project Documentation

This directory contains all official documentation for the PICU (Personal Investment & Cryptocurrency Understanding) project. The structure is based on international software engineering standards such as ISO/IEC 12207 and SPICE (ISO/IEC 15504) to ensure clarity, maintainability, and completeness.

## Documentation Structure

The documentation is organized by software lifecycle process areas. All new documents should be placed in the appropriate subdirectory.

- **`00_Project_Management/`**: Documents related to project planning, execution, and control.

  - `01_Plans/`: Project plans, roadmaps, strategies, and resource management.
  - `02_Reports/`: Progress reports, analysis reports, and review outcomes.
  - `03_Meetings/`: Meeting agendas, minutes, and action items.

- **`01_Requirements_Analysis/`**: Documents defining what the system should do.

  - `01_Stakeholder_Requirements/`: Needs and requirements from the user's perspective.
  - `02_System_Requirements_Specification/`: Detailed functional and non-functional system requirements.
  - `03_Use_Cases/`: User stories and scenarios.

- **`02_Design_and_Architecture/`**: Documents describing how the system is designed and constructed.

  - `01_Software_Architecture_Design/`: High-level system architecture, component diagrams, and data flow.
  - `02_Database_Design/`: Database schemas, ERDs, and data dictionary.
  - `03_UI_UX_Design/`: Wireframes, mockups, and user interface guidelines.
  - `04_API_Specification/`: Detailed specifications for internal and external APIs.

- **`03_Implementation/`**: Documents supporting the coding and development process.

  - `01_Coding_Conventions/`: Coding standards and style guides.
  - `02_Development_Environment_Setup/`: Guides for setting up a local development environment.
  - `03_Module_Specifications/`: Detailed design for specific modules or components.

- **`04_Verification_and_Validation/`**: Documents related to testing and quality assurance.

  - `01_Test_Plan/`: Overall testing strategy and plan.
  - `02_Test_Cases/`: Specific test cases for system features.
  - `03_Test_Reports/`: Results from test execution cycles.
  - `04_Code_Reviews/`: Guidelines and records of code reviews.

- **`05_Deployment_and_Release/`**: Documents concerning the build, release, and deployment of the software.

  - `01_Deployment_Guide/`: Instructions for deploying the application to production or other environments.
  - `02_Release_Notes/`: A summary of changes for each version release.
  - `03_Infrastructure_Configuration/`: Details about the server, network, and cloud infrastructure.

- **`06_Operations_and_Maintenance/`**: Documents for the ongoing operation and maintenance of the system.
  - `01_User_Manual/`: Guides for end-users or system administrators.
  - `02_Troubleshooting_Guide/`: Manuals for diagnosing and fixing common problems.
  - `03_Service_Monitoring/`: Information on how the system is monitored.

## 빠른 참조 (Quick Reference)

### 📋 설정 및 구성 (Configuration)

- **설정 파일 관리**: [`02_Design_and_Architecture/01_Software_Architecture_Design/CONFIG_파일_동적생성_및_템플릿_관리_전수조사_보고서.md`](02_Design_and_Architecture/01_Software_Architecture_Design/CONFIG_파일_동적생성_및_템플릿_관리_전수조사_보고서.md)
- **Config 관리 리뷰**: [`04_Verification_and_Validation/04_Code_Reviews/CONFIG_MANAGEMENT_REVIEW.md`](04_Verification_and_Validation/04_Code_Reviews/CONFIG_MANAGEMENT_REVIEW.md)
- **GUI 설정 분석**: [`00_Project_Management/02_Reports/GUI_CONFIGURATION_ANALYSIS.md`](00_Project_Management/02_Reports/GUI_CONFIGURATION_ANALYSIS.md)
- **GUI 설정 개선**: [`02_Design_and_Architecture/03_UI_UX_Design/GUI_설정_및_에러처리_개선_보고서.md`](02_Design_and_Architecture/03_UI_UX_Design/GUI_설정_및_에러처리_개선_보고서.md)

### 🚀 배포 및 설치 (Deployment & Setup)

- **배포 가이드**: [`05_Deployment_and_Release/01_Deployment_Guide/DEPLOYMENT_GUIDE.md`](05_Deployment_and_Release/01_Deployment_Guide/DEPLOYMENT_GUIDE.md)
- **자동화 가이드**: [`05_Deployment_and_Release/01_Deployment_Guide/AUTOMATION_GUIDE.md`](05_Deployment_and_Release/01_Deployment_Guide/AUTOMATION_GUIDE.md)
- **라즈베리파이 설정**: [`03_Implementation/02_Development_Environment_Setup/RASPBERRY_PI_SETUP_WORKFLOW.md`](03_Implementation/02_Development_Environment_Setup/RASPBERRY_PI_SETUP_WORKFLOW.md)
- **배포 구조 분석**: [`02_Design_and_Architecture/01_Software_Architecture_Design/DEPLOYMENT_STRUCTURE_ANALYSIS.md`](02_Design_and_Architecture/01_Software_Architecture_Design/DEPLOYMENT_STRUCTURE_ANALYSIS.md)

### 🔧 트러블슈팅 (Troubleshooting)

- **시스템 리소스 관리**: [`06_Operations_and_Maintenance/02_Troubleshooting_Guide/시스템_리소스_관리_계획.md`](06_Operations_and_Maintenance/02_Troubleshooting_Guide/시스템_리소스_관리_계획.md)
- **파이프라인 문제**: [`06_Operations_and_Maintenance/02_Troubleshooting_Guide/PIPELINE_data_문제_분석_보고서.md`](06_Operations_and_Maintenance/02_Troubleshooting_Guide/PIPELINE_data_문제_분석_보고서.md)
- **HDFS 문제**: [`06_Operations_and_Maintenance/02_Troubleshooting_Guide/HDFS_연동_문제_분석_보고서.md`](06_Operations_and_Maintenance/02_Troubleshooting_Guide/HDFS_연동_문제_분석_보고서.md)
- **GUI 실행 문제**: [`06_Operations_and_Maintenance/02_Troubleshooting_Guide/GUI_실행_문제_분석_보고서.md`](06_Operations_and_Maintenance/02_Troubleshooting_Guide/GUI_실행_문제_분석_보고서.md)
- **수동 파이프라인 실행**: [`06_Operations_and_Maintenance/02_Troubleshooting_Guide/Manual_Pipeline_Execution_Guide.md`](06_Operations_and_Maintenance/02_Troubleshooting_Guide/Manual_Pipeline_Execution_Guide.md)
- **Python 경로 통합**: [`06_Operations_and_Maintenance/02_Troubleshooting_Guide/PYTHONPATH_UNIFICATION_2025-12-03.md`](06_Operations_and_Maintenance/02_Troubleshooting_Guide/PYTHONPATH_UNIFICATION_2025-12-03.md)

### 🏗️ 아키텍처 및 설계 (Architecture & Design)

- **파이프라인 아키텍처**: [`02_Design_and_Architecture/01_Software_Architecture_Design/파이프라인_ 아키텍처_설계.md`](02*Design_and_Architecture/01_Software_Architecture_Design/파이프라인* 아키텍처\_설계.md)
- **HDFS 설계**: [`02_Design_and_Architecture/01_Software_Architecture_Design/HDFS_설계_및_파이프라인연결_로직_보고서.md`](02_Design_and_Architecture/01_Software_Architecture_Design/HDFS_설계_및_파이프라인연결_로직_보고서.md)
- **HDFS 프로세스 플로우**: [`02_Design_and_Architecture/01_Software_Architecture_Design/HDFS_PROCESS_FLOW_ANALYSIS.md`](02_Design_and_Architecture/01_Software_Architecture_Design/HDFS_PROCESS_FLOW_ANALYSIS.md)
- **통합 가이드**: [`02_Design_and_Architecture/01_Software_Architecture_Design/INTEGRATION_GUIDE.md`](02_Design_and_Architecture/01_Software_Architecture_Design/INTEGRATION_GUIDE.md)

### 📊 모듈 및 구현 (Modules & Implementation)

- **Kafka Consumer**: [`03_Implementation/03_Module_Specifications/Kafka_Consumer_Hybrid_Pattern_Implementation.md`](03_Implementation/03_Module_Specifications/Kafka_Consumer_Hybrid_Pattern_Implementation.md)
- **Control Tab**: [`03_Implementation/03_Module_Specifications/CONTROL_제어_TAB_module_보고서.md`](03_Implementation/03_Module_Specifications/CONTROL_제어_TAB_module_보고서.md)
- **MapReduce 비교**: [`02_Design_and_Architecture/01_Software_Architecture_Design/MAPREDUCE_SCRIPTS_COMPARISON.md`](02_Design_and_Architecture/01_Software_Architecture_Design/MAPREDUCE_SCRIPTS_COMPARISON.md)

### 📝 사용자 가이드 (User Guides)

- **GUI 가이드**: [`06_Operations_and_Maintenance/01_User_Manual/GUI_GUIDE.md`](06_Operations_and_Maintenance/01_User_Manual/GUI_GUIDE.md)

### ✅ 테스트 및 검증 (Testing & Validation)

- **GUI 테스트**: [`04_Verification_and_Validation/03_Test_Reports/GUI_테스트_호출_분석_보고서.md`](04_Verification_and_Validation/03_Test_Reports/GUI_테스트_호출_분석_보고서.md)
- **요구사항 검증**: [`04_Verification_and_Validation/03_Test_Reports/REQUIREMENTS_VERIFICATION_REPORT.md`](04_Verification_and_Validation/03_Test_Reports/REQUIREMENTS_VERIFICATION_REPORT.md)
- **HDFS 로직 리뷰**: [`04_Verification_and_Validation/04_Code_Reviews/HDFS_LOGIC_REVIEW.md`](04_Verification_and_Validation/04_Code_Reviews/HDFS_LOGIC_REVIEW.md)

### 📈 프로젝트 관리 (Project Management)

- **개발 로드맵**: [`00_Project_Management/01_Plans/DEVELOPMENT_ROADMAP.md`](00_Project_Management/01_Plans/DEVELOPMENT_ROADMAP.md)
- **실행 계획**: [`00_Project_Management/01_Plans/EXECUTION_PLAN.md`](00_Project_Management/01_Plans/EXECUTION_PLAN.md)
- **종합 분석**: [`00_Project_Management/02_Reports/COMPREHENSIVE_ANALYSIS.md`](00_Project_Management/02_Reports/COMPREHENSIVE_ANALYSIS.md)

---

## Contribution

When adding a new document, please place it in the most relevant folder. If a suitable folder does not exist, consult with the project lead before creating a new one.
