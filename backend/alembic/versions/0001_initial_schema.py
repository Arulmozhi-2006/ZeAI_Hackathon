# """initial schema

# Revision ID: 0001
# Revises:
# Create Date: 2026-06-25

# """
# import sqlalchemy as sa
# from alembic import op
# from sqlalchemy.dialects import postgresql

# revision = "0001"
# down_revision = None
# branch_labels = None
# depends_on = None


# def upgrade() -> None:
#     op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

#     user_role = postgresql.ENUM(
#     "admin", "analyst", "viewer",
#     name="user_role",
#     create_type=False
# )

#     prompt_status = postgresql.ENUM(
#     "PENDING", "PROCESSED", "ERROR",
#     name="prompt_status",
#     create_type=False
# )

#     decision_type = postgresql.ENUM(
#     "ALLOW", "BLOCK",
#     name="decision_type",
#     create_type=False
# )

#     severity_level = postgresql.ENUM(
#     "LOW", "MEDIUM", "HIGH", "CRITICAL",
#     name="severity_level",
#     create_type=False
# )

#     user_role.create(op.get_bind(), checkfirst=True)
#     prompt_status.create(op.get_bind(), checkfirst=True)
#     decision_type.create(op.get_bind(), checkfirst=True)
#     severity_level.create(op.get_bind(), checkfirst=True)

#     op.create_table(
#         "users",
#         sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
#         sa.Column("email", sa.String(255), nullable=False, unique=True),
#         sa.Column("hashed_password", sa.String(255), nullable=False),
#         sa.Column("full_name", sa.String(255), nullable=True),
#         sa.Column("role", user_role, nullable=False, server_default="viewer"),
#         sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
#         sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#         sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#     )
#     op.create_index("ix_users_email", "users", ["email"])

#     op.create_table(
#         "threat_categories",
#         sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
#         sa.Column("name", sa.String(100), nullable=False, unique=True),
#         sa.Column("description", sa.String(500), nullable=True),
#         sa.Column("default_severity", sa.String(20), nullable=False, server_default="LOW"),
#     )

#     op.create_table(
#         "api_keys",
#         sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
#         sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
#         sa.Column("key_hash", sa.String(255), nullable=False, unique=True),
#         sa.Column("key_prefix", sa.String(16), nullable=False),
#         sa.Column("name", sa.String(255), nullable=False),
#         sa.Column("scopes", postgresql.JSONB, nullable=False, server_default="{}"),
#         sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
#         sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
#         sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
#         sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#         sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#     )
#     op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])

#     op.create_table(
#         "prompt_logs",
#         sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
#         sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
#         sa.Column("api_key_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_keys.id", ondelete="SET NULL"), nullable=True),
#         sa.Column("raw_prompt", sa.Text, nullable=False),
#         sa.Column("prompt_hash", sa.String(64), nullable=False),
#         sa.Column("source_ip", sa.String(64), nullable=True),
#         sa.Column("user_agent", sa.String(500), nullable=True),
#         sa.Column("status", prompt_status, nullable=False, server_default="PENDING"),
#         sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#         sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#     )
#     op.create_index("ix_prompt_logs_prompt_hash", "prompt_logs", ["prompt_hash"])
#     op.create_index("ix_prompt_logs_created_at", "prompt_logs", ["created_at"])

#     op.create_table(
#         "model_predictions",
#         sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
#         sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
#         sa.Column("model_version", sa.String(100), nullable=False),
#         sa.Column("embedding_vector", postgresql.JSONB, nullable=True),
#         sa.Column("predicted_category_id", sa.Integer, sa.ForeignKey("threat_categories.id"), nullable=False),
#         sa.Column("confidence_score", sa.Float, nullable=False),
#         sa.Column("raw_model_output", postgresql.JSONB, nullable=True),
#         sa.Column("inference_time_ms", sa.Float, nullable=True),
#         sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#     )

#     op.create_table(
#         "detection_results",
#         sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
#         sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
#         sa.Column("model_prediction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("model_predictions.id", ondelete="CASCADE"), nullable=False),
#         sa.Column("final_category_id", sa.Integer, sa.ForeignKey("threat_categories.id"), nullable=False),
#         sa.Column("risk_score", sa.Float, nullable=False),
#         sa.Column("classification_reason", sa.Text, nullable=True),
#         sa.Column("threat_explanation", sa.Text, nullable=True),
#         sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#     )
#     op.create_index("ix_detection_results_risk_score", "detection_results", ["risk_score"])

#     op.create_table(
#         "firewall_decisions",
#         sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
#         sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
#         sa.Column("detection_result_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("detection_results.id", ondelete="CASCADE"), nullable=True),
#         sa.Column("decision", decision_type, nullable=False),
#         sa.Column("policy_rule_triggered", sa.String(255), nullable=True),
#         sa.Column("decision_reason", sa.Text, nullable=True),
#         sa.Column("llm_provider", sa.String(50), nullable=True),
#         sa.Column("llm_forwarded", sa.Boolean, nullable=False, server_default=sa.false()),
#         sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#     )

#     op.create_table(
#         "threat_logs",
#         sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
#         sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
#         sa.Column("threat_category_id", sa.Integer, sa.ForeignKey("threat_categories.id"), nullable=False),
#         sa.Column("severity", severity_level, nullable=False),
#         sa.Column("risk_score", sa.Float, nullable=False),
#         sa.Column("blocked", sa.Boolean, nullable=False, server_default=sa.false()),
#         sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#     )
#     op.create_index("ix_threat_logs_severity_created_at", "threat_logs", ["severity", "created_at"])

#     op.create_table(
#         "llm_responses",
#         sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
#         sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
#         sa.Column("provider", sa.String(50), nullable=False, server_default="gemini"),
#         sa.Column("response_text", sa.Text, nullable=True),
#         sa.Column("latency_ms", sa.Float, nullable=True),
#         sa.Column("token_usage", postgresql.JSONB, nullable=True),
#         sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#     )

#     op.create_table(
#         "audit_trail",
#         sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
#         sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
#         sa.Column("action_type", sa.String(100), nullable=False),
#         sa.Column("resource_type", sa.String(100), nullable=True),
#         sa.Column("resource_id", sa.String(100), nullable=True),
#         sa.Column("ip_address", sa.String(64), nullable=True),
#         sa.Column("metadata_json", postgresql.JSONB, nullable=True),
#         sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
#     )

#     op.create_table(
#         "analytics_daily",
#         sa.Column("date", sa.Date, primary_key=True),
#         sa.Column("total_requests", sa.Integer, nullable=False, server_default="0"),
#         sa.Column("total_allowed", sa.Integer, nullable=False, server_default="0"),
#         sa.Column("total_blocked", sa.Integer, nullable=False, server_default="0"),
#         sa.Column("top_category_id", sa.Integer, nullable=True),
#         sa.Column("avg_risk_score", sa.Float, nullable=True),
#         sa.Column("avg_confidence_score", sa.Float, nullable=True),
#     )


# def downgrade() -> None:
#     op.drop_table("analytics_daily")
#     op.drop_table("audit_trail")
#     op.drop_table("llm_responses")
#     op.drop_table("threat_logs")
#     op.drop_table("firewall_decisions")
#     op.drop_table("detection_results")
#     op.drop_table("model_predictions")
#     op.drop_table("prompt_logs")
#     op.drop_table("api_keys")
#     op.drop_table("threat_categories")
#     op.drop_table("users")

#     sa.Enum(name="severity_level").drop(op.get_bind(), checkfirst=True)
#     sa.Enum(name="decision_type").drop(op.get_bind(), checkfirst=True)
#     sa.Enum(name="prompt_status").drop(op.get_bind(), checkfirst=True)
#     sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    user_role = postgresql.ENUM(
        "admin", "analyst", "viewer",
        name="user_role",
        create_type=False
    )

    prompt_status = postgresql.ENUM(
        "PENDING", "PROCESSED", "ERROR",
        name="prompt_status",
        create_type=False
    )

    decision_type = postgresql.ENUM(
        "ALLOW", "BLOCK",
        name="decision_type",
        create_type=False
    )

    severity_level = postgresql.ENUM(
        "LOW", "MEDIUM", "HIGH", "CRITICAL",
        name="severity_level",
        create_type=False
    )

    user_role.create(op.get_bind(), checkfirst=True)
    prompt_status.create(op.get_bind(), checkfirst=True)
    decision_type.create(op.get_bind(), checkfirst=True)
    severity_level.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", user_role, nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "threat_categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("default_severity", sa.String(20), nullable=False, server_default="LOW"),
    )

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("key_prefix", sa.String(16), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("scopes", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])

    op.create_table(
        "prompt_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("api_key_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_keys.id", ondelete="SET NULL"), nullable=True),
        sa.Column("raw_prompt", sa.Text, nullable=False),
        sa.Column("prompt_hash", sa.String(64), nullable=False),
        sa.Column("source_ip", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("status", prompt_status, nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_prompt_logs_prompt_hash", "prompt_logs", ["prompt_hash"])
    op.create_index("ix_prompt_logs_created_at", "prompt_logs", ["created_at"])

    op.create_table(
        "model_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column("embedding_vector", postgresql.JSONB, nullable=True),
        sa.Column("predicted_category_id", sa.Integer, sa.ForeignKey("threat_categories.id"), nullable=False),
        sa.Column("confidence_score", sa.Float, nullable=False),
        sa.Column("raw_model_output", postgresql.JSONB, nullable=True),
        sa.Column("inference_time_ms", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "detection_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_prediction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("model_predictions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("final_category_id", sa.Integer, sa.ForeignKey("threat_categories.id"), nullable=False),
        sa.Column("risk_score", sa.Float, nullable=False),
        sa.Column("classification_reason", sa.Text, nullable=True),
        sa.Column("threat_explanation", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_detection_results_risk_score", "detection_results", ["risk_score"])

    op.create_table(
        "firewall_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("detection_result_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("detection_results.id", ondelete="CASCADE"), nullable=True),
        sa.Column("decision", decision_type, nullable=False),
        sa.Column("policy_rule_triggered", sa.String(255), nullable=True),
        sa.Column("decision_reason", sa.Text, nullable=True),
        sa.Column("llm_provider", sa.String(50), nullable=True),
        sa.Column("llm_forwarded", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "threat_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("threat_category_id", sa.Integer, sa.ForeignKey("threat_categories.id"), nullable=False),
        sa.Column("severity", severity_level, nullable=False),
        sa.Column("risk_score", sa.Float, nullable=False),
        sa.Column("blocked", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_threat_logs_severity_created_at", "threat_logs", ["severity", "created_at"])

    op.create_table(
        "llm_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prompt_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompt_logs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False, server_default="gemini"),
        sa.Column("response_text", sa.Text, nullable=True),
        sa.Column("latency_ms", sa.Float, nullable=True),
        sa.Column("token_usage", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "audit_trail",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "analytics_daily",
        sa.Column("date", sa.Date, primary_key=True),
        sa.Column("total_requests", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_allowed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_blocked", sa.Integer, nullable=False, server_default="0"),
        sa.Column("top_category_id", sa.Integer, nullable=True),
        sa.Column("avg_risk_score", sa.Float, nullable=True),
        sa.Column("avg_confidence_score", sa.Float, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("analytics_daily")
    op.drop_table("audit_trail")
    op.drop_table("llm_responses")
    op.drop_table("threat_logs")
    op.drop_table("firewall_decisions")
    op.drop_table("detection_results")
    op.drop_table("model_predictions")
    op.drop_table("prompt_logs")
    op.drop_table("api_keys")
    op.drop_table("threat_categories")
    op.drop_table("users")

    sa.Enum(name="severity_level").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="decision_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="prompt_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
