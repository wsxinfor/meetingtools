"""meeting_templates table with seed data

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-29

"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_GENERAL_PROMPT = """\
请根据以下会议转写内容，生成清晰、简洁、可执行的会议纪要。

输出结构：

# 会议摘要
# 讨论事项
# 形成结论
# 行动项
# 风险与问题
# 后续计划

要求：
- 不编造信息
- 不确定的信息标注"待确认"
- 行动项尽量包含负责人和时间

会议转写内容：

{{transcript_text}}\
"""

_PRESALES_PROMPT = """\
你是一名资深IT售前顾问。请根据会议转写内容，提取结构化售前信息，形成会议纪要。

输出结构：

# 会议摘要

用3-5句话概括本次会议。

# 客户基本信息

- 客户名称：
- 所属行业：
- 参会人员：
- 我方人员：

# 客户当前IT现状

包括服务器、存储、网络、安全、虚拟化、云平台等信息。

# 明确需求

逐条列出客户明确表达的需求。

# 潜在痛点

根据会议内容推断，标注"推断"。

# 涉及产品/方案

列出会议中提到的产品、品牌、方案方向。

# 预算与采购信息

- 预算：
- 采购方式：
- 时间计划：
- 项目阶段：

# 风险点

包括预算、竞争对手、技术不确定性、采购流程等。

# 下一步行动项

| 事项 | 负责人 | 截止时间 | 备注 |
|---|---|---|---|

# 待确认问题

列出下次沟通需要确认的问题。

会议转写内容：

{{transcript_text}}\
"""

_PROJECT_PROMPT = """\
请根据以下项目推进会议转写内容，生成项目进展纪要。

输出结构：

# 会议摘要

# 各议题进展

逐项列出会议讨论的议题及当前状态（进行中/已完成/待启动/已阻塞）。

# 已完成事项

本期已完成的里程碑或任务。

# 当前阻塞与风险

逐条列出阻塞原因、影响范围和解决方向。

# 行动项

| 事项 | 负责人 | 截止时间 | 优先级 |
|---|---|---|---|

# 下次会议安排

- 时间：
- 议题：

会议转写内容：

{{transcript_text}}\
"""

_TECHNICAL_PROMPT = """\
请根据以下技术方案讨论会议转写内容，生成技术纪要。

输出结构：

# 会议摘要

# 讨论背景

描述本次技术讨论的背景和目标。

# 技术方案概述

列出讨论中涉及的主要方案或架构。

# 方案对比

如存在多个方案，列出各方案的优缺点对比。

# 技术决策

明确的技术决策或选型结论，标注决策理由。

# 待解决技术问题

列出尚未解决或需进一步验证的技术问题。

# 行动项

| 事项 | 负责人 | 截止时间 |
|---|---|---|

会议转写内容：

{{transcript_text}}\
"""

_BIDDING_PROMPT = """\
请根据以下招投标沟通会议转写内容，生成招投标跟进纪要。

输出结构：

# 会议摘要

# 项目基本信息

- 项目名称：
- 采购单位：
- 预算规模：
- 采购方式：（公开招标/竞争性谈判/单一来源/等）

# 当前阶段

描述项目当前所处的招标阶段。

# 竞争态势

已知参与竞争的厂商及优劣势分析。

# 我方参与策略

包括技术路线、商务策略、合作资源等。

# 关键需求与评分关注点

列出招标文件或客户明示的关键评分项。

# 风险点

包括政策、资质、竞争对手、价格等风险。

# 行动项

| 事项 | 负责人 | 截止时间 |
|---|---|---|

# 待确认信息

会议转写内容：

{{transcript_text}}\
"""

_DEFAULT_TEMPLATES = [
    {
        "id": str(uuid.uuid4()),
        "name": "通用会议纪要",
        "type": "general",
        "description": "适用于各类通用内部会议，输出标准结构化纪要",
        "prompt_text": _GENERAL_PROMPT,
        "enabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "售前客户交流",
        "type": "presales",
        "description": "适用于IT售前与客户的交流会议，提取客户需求、现状和行动项",
        "prompt_text": _PRESALES_PROMPT,
        "enabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "项目推进会议",
        "type": "project",
        "description": "适用于项目例会，跟踪进展、阻塞和行动项",
        "prompt_text": _PROJECT_PROMPT,
        "enabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "技术方案讨论",
        "type": "technical",
        "description": "适用于技术评审和方案讨论会议，记录技术决策和待解决问题",
        "prompt_text": _TECHNICAL_PROMPT,
        "enabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "招投标沟通",
        "type": "bidding",
        "description": "适用于招投标前期沟通，梳理竞争态势和参与策略",
        "prompt_text": _BIDDING_PROMPT,
        "enabled": True,
    },
]


def upgrade() -> None:
    op.create_table(
        "meeting_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("prompt_text", sa.Text, nullable=False),
        sa.Column("output_schema", JSONB),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    templates_table = sa.table(
        "meeting_templates",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("type", sa.String),
        sa.column("description", sa.Text),
        sa.column("prompt_text", sa.Text),
        sa.column("enabled", sa.Boolean),
    )
    op.bulk_insert(templates_table, _DEFAULT_TEMPLATES)


def downgrade() -> None:
    op.drop_table("meeting_templates")
