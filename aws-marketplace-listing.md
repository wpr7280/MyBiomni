# WarpHelix — AWS Marketplace Product Listing

> All required fields for AWS Marketplace AMI listing

---

## 1. Product Title

**WarpHelix: AI-Powered Biomedical Research Assistant**

---

## 2. Short Description (max 200 characters)

AI research assistant for biomedical scientists. 22 skill domains, 200+ specialized tools, natural language interface. Built on the Biomni framework from Stanford SNAP Lab.

---

## 3. Long Description (Product Overview)

### WarpHelix: Your AI Lab Partner for Biomedical Research

WarpHelix is a self-hosted AI research assistant purpose-built for biomedical scientists. It combines large language models with 200+ domain-specific computational tools across 22 scientific disciplines — from molecular biology and genomics to pharmacology and bioimaging.

**How It Works**

Ask questions in natural language. WarpHelix automatically selects the right tools, writes and executes code, queries biological databases, and delivers publication-ready results — all within a secure, private environment running entirely on your AWS infrastructure.

**Key Capabilities**

- **22 Skill Domains**: Biochemistry, genetics, cell biology, pharmacology, immunology, pathology, bioimaging, systems biology, synthetic biology, and more
- **200+ Specialized Tools**: Enzyme kinetics analysis, molecular docking (AutoDock Vina, DiffDock), CRISPR sgRNA design, single-cell annotation, protein structure prediction, literature search, and beyond
- **Know-How System**: Built-in expert protocols and best-practice workflows (e.g., three-tiered sgRNA design guide, single-cell annotation pipeline)
- **Natural Language Interface**: No coding required — describe your research question and WarpHelix handles tool selection, code generation, and execution
- **Admin Portal**: Full web-based management for skills, know-how documents, user accounts, model configuration, and usage monitoring
- **Multi-Model Support**: Works with Amazon Bedrock (Claude, Titan), OpenAI, Anthropic, Google Gemini, Azure OpenAI, and custom endpoints
- **Sandboxed Execution**: Code runs in isolated environments for security and reproducibility

**Architecture**

- **Agent Backend**: Python FastAPI with LangChain-based tool orchestration
- **Admin Backend**: Java Spring Boot for user management, quotas, and configuration
- **Frontend**: Vue.js admin portal + user-facing chat interface
- **Database**: MySQL 8.0 for persistent storage, Redis for caching
- **Reverse Proxy**: Nginx with SSL-ready configuration

**Who Is This For?**

- Biomedical researchers and lab scientists
- Bioinformatics teams
- Pharmaceutical R&D departments
- University research groups
- Biotech startups

**Open Source Foundation**

WarpHelix is built on the [Biomni framework](https://github.com/snap-stanford/biomni) from Stanford SNAP Lab (Apache 2.0 License). We extend it with a production-ready deployment stack, admin management system, skill/know-how management, and enterprise features.

---

## 4. Product Logo

- File: `warphelix-aws-1x1.png` (640×640, white background)
- Alt: `warphelix-aws-2x1.png` (640×320, white background)

---

## 5. Highlights (up to 3 bullet points shown on search results)

1. **200+ biomedical AI tools** across 22 scientific domains — from molecular docking to single-cell annotation
2. **Natural language interface** — describe your research question, get executable results
3. **Self-hosted & private** — runs entirely on your AWS infrastructure, no data leaves your account

---

## 6. Product Categories

- **Primary**: Machine Learning
- **Secondary**: Life Sciences
- **Tertiary**: Research & Technical Computing

---

## 7. Search Keywords

`biomedical AI`, `research assistant`, `bioinformatics`, `molecular biology`, `drug discovery`, `CRISPR`, `genomics`, `protein analysis`, `single cell`, `lab automation`, `LLM agent`

---

## 8. Support Information

### Support Description

Community support via GitHub Issues. Email support available at peirongw@foxmail.com. Documentation included in the AMI at `/opt/biomni/docs/`.

### Support Resources

| Resource | URL |
|----------|-----|
| Documentation | Included in AMI (`/opt/biomni/docs/`) |
| Source Code | https://github.com/wpr7280/MyBiomni |
| Issue Tracker | https://github.com/wpr7280/MyBiomni/issues |
| Email Support | peirongw@foxmail.com |

### Refund Policy

This is a free (BYOL) AMI. No charges from Warp Drive Technology. You only pay for AWS infrastructure costs (EC2, EBS, data transfer).

---

## 9. Pricing

### Pricing Model: Free / BYOL (Bring Your Own License)

- **Software charges**: $0.00 (Free)
- **Infrastructure charges**: Standard AWS EC2 pricing applies
- **LLM API costs**: User provides their own API keys (Bedrock, OpenAI, etc.)

---

## 10. Instance Type Recommendations

| Size | Instance Type | vCPU | RAM | Use Case |
|------|--------------|------|-----|----------|
| Minimum | t3.large | 2 | 8 GB | Light testing |
| **Recommended** | **t3.xlarge** | **4** | **16 GB** | Production use |
| Performance | m6i.xlarge | 4 | 16 GB | Heavy workloads |
| Heavy | m6i.2xlarge | 8 | 32 GB | Multiple concurrent users |

**Storage**: Minimum 30 GB gp3 EBS (50 GB recommended)

---

## 11. Operating System

Ubuntu 24.04 LTS (arm64 / Graviton compatible)

---

## 12. Usage Instructions

### Quick Start

1. Launch an EC2 instance from this AMI (t3.xlarge recommended, 30GB+ EBS)
2. Open Security Group ports: **80** (HTTP), **443** (HTTPS), **22** (SSH)
3. Wait 2-3 minutes for first-boot initialization
4. Access the **Admin Portal** at `http://<instance-ip>/admin/`
5. Login credentials are in `~/biomni-credentials.txt` (SSH to instance to view)
6. Configure your LLM provider (Amazon Bedrock, OpenAI, etc.) in Admin → System Config → Model Configuration
7. Access the **Chat Interface** at `http://<instance-ip>/`

### First Login

- Default admin requires password change on first login
- Configure at least one LLM API key before using the chat interface

### SSH Access

```
ssh -i your-key.pem ubuntu@<instance-ip>
cat ~/biomni-credentials.txt
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| Nginx | 80/443 | Reverse proxy |
| Admin Backend | 9999 | Spring Boot API |
| Agent Backend | 8000 | FastAPI + AI Agent |
| MySQL | 3306 | Database (local only) |
| Redis | 6379 | Cache (local only) |

### Security Recommendations

- Enable HTTPS with your own SSL certificate (Nginx config at `/etc/nginx/sites-available/biomni`)
- Restrict SSH access to your IP range
- Change the default admin password immediately
- Store API keys securely via the Admin Portal (encrypted in database)

---

## 13. Version Information

- **Product Version**: 2.0.0
- **Biomni Framework Version**: Latest (Stanford SNAP Lab)
- **Release Date**: April 2026
- **What's New in v2.0**:
  - Skill management system (22 domains, 200+ tools)
  - Know-How management (expert protocols & workflows)
  - Admin portal with full i18n (English/Chinese)
  - Dynamic skill/know-how hot-reload
  - Improved markdown rendering with `marked`

---

## 14. Seller Information

- **Company Name**: Warp Drive Technology
- **Website**: https://warp-driver-tech.github.io
- **Contact**: peirongw@foxmail.com

---

## 15. Legal / EULA

### End User License Agreement

This AMI contains open-source software licensed under Apache 2.0 (Biomni framework) and other permissive licenses. The WarpHelix extensions are provided under the MIT License.

By launching this AMI, you agree to:
1. Comply with all applicable open-source licenses
2. Provide your own LLM API keys and accept the terms of your chosen LLM provider
3. Accept that software is provided "as is" without warranty

### Attribution

Built on the [Biomni](https://github.com/snap-stanford/biomni) framework by Stanford SNAP Lab. Citation: Huang, Q. et al. "Biomni: A Biomedical Multi-Tool Agent System." Stanford SNAP Lab, 2024.

---

## 16. Architecture Diagram (for Product Detail page)

```
┌─────────────────────────────────────────────┐
│                   Nginx (80/443)             │
│         Reverse Proxy + Static Files        │
├──────────┬──────────────┬───────────────────┤
│          │              │                   │
│  Admin   │   Client     │    API Router     │
│  Portal  │   Chat UI    │                   │
│  (Vue)   │   (Vue)      │  /api/* → Spring  │
│          │              │  /api/skills → Agent
│          │              │  /api/knowhow → Agent
│          │              │  /ws → Agent      │
├──────────┴──────────────┴───────────────────┤
│                                             │
│  ┌─────────────┐    ┌────────────────────┐  │
│  │ Admin Backend│    │  Agent Backend     │  │
│  │ Spring Boot │    │  FastAPI + LangChain│ │
│  │ (Port 9999) │    │  (Port 8000)       │  │
│  └──────┬──────┘    └────────┬───────────┘  │
│         │                    │               │
│         ▼                    ▼               │
│  ┌─────────────┐    ┌────────────────────┐  │
│  │  MySQL 8.0  │    │  LLM Provider      │  │
│  │  + Redis    │    │  (Bedrock/OpenAI/  │  │
│  │             │    │   Anthropic/etc.)  │  │
│  └─────────────┘    └────────────────────┘  │
└─────────────────────────────────────────────┘
```
