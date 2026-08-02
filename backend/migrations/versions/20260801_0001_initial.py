"""Initial GROE schema
Revision ID: 20260801_0001
Revises:
"""
from alembic import op
import sqlalchemy as sa
revision="20260801_0001"
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("users",
        sa.Column("id",sa.String(36),primary_key=True),sa.Column("email",sa.String(320),nullable=False),sa.Column("password_hash",sa.String(512),nullable=False),sa.Column("preferred_language",sa.String(5),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.UniqueConstraint("email"))
    op.create_index("ix_users_email","users",["email"],unique=True)
    op.create_table("species",
        sa.Column("id",sa.String(36),primary_key=True),sa.Column("scientific_name",sa.String(255),nullable=False),sa.Column("taxonomy_source",sa.String(500),nullable=False),sa.UniqueConstraint("scientific_name"))
    op.create_index("ix_species_scientific_name","species",["scientific_name"],unique=True)
    op.create_table("crop_profiles",
        sa.Column("id",sa.String(36),primary_key=True),sa.Column("species_id",sa.String(36),sa.ForeignKey("species.id"),nullable=False),sa.Column("slug",sa.String(120),nullable=False),sa.Column("cultivar_group",sa.String(255)),sa.Column("name_en",sa.String(120),nullable=False),sa.Column("name_id",sa.String(120),nullable=False),sa.Column("alternative_names_en",sa.JSON(),nullable=False),sa.Column("alternative_names_id",sa.JSON(),nullable=False),sa.Column("category",sa.String(60),nullable=False),sa.Column("edible_parts",sa.JSON(),nullable=False),sa.Column("annual_or_perennial",sa.String(30),nullable=False),sa.Column("parameters",sa.JSON(),nullable=False),sa.Column("guidance_en",sa.JSON(),nullable=False),sa.Column("guidance_id",sa.JSON(),nullable=False),sa.Column("source_metadata",sa.JSON(),nullable=False),sa.Column("verification_status",sa.String(50),nullable=False),sa.Column("confidence_level",sa.String(20),nullable=False),sa.Column("fields_requiring_review",sa.JSON(),nullable=False),sa.Column("active",sa.Boolean(),nullable=False),sa.UniqueConstraint("slug",name="uq_crop_slug"))
    op.create_index("ix_crop_profiles_species_id","crop_profiles",["species_id"])
    op.create_index("ix_crop_profiles_slug","crop_profiles",["slug"])
    op.create_index("ix_crop_profiles_category","crop_profiles",["category"])
    op.create_index("ix_crop_profiles_active","crop_profiles",["active"])
    op.create_table("saved_plans",
        sa.Column("id",sa.String(36),primary_key=True),sa.Column("user_id",sa.String(36),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("name",sa.String(160),nullable=False),sa.Column("language",sa.String(5),nullable=False),sa.Column("planner_input",sa.JSON(),nullable=False),sa.Column("plan_data",sa.JSON(),nullable=False),sa.Column("share_slug",sa.String(48),nullable=False),sa.Column("is_public",sa.Boolean(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False),sa.UniqueConstraint("share_slug"))
    op.create_index("ix_saved_plans_user_id","saved_plans",["user_id"])
    op.create_index("ix_saved_plans_share_slug","saved_plans",["share_slug"],unique=True)
    op.create_table("refresh_tokens",
        sa.Column("id",sa.String(36),primary_key=True),sa.Column("user_id",sa.String(36),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("token_hash",sa.String(128),nullable=False),sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),sa.Column("revoked",sa.Boolean(),nullable=False),sa.UniqueConstraint("token_hash"))
    op.create_index("ix_refresh_tokens_user_id","refresh_tokens",["user_id"])
    op.create_index("ix_refresh_tokens_token_hash","refresh_tokens",["token_hash"],unique=True)
    op.create_table("diary_entries",
        sa.Column("id",sa.String(36),primary_key=True),sa.Column("user_id",sa.String(36),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("plan_id",sa.String(36),sa.ForeignKey("saved_plans.id",ondelete="CASCADE"),nullable=False),sa.Column("crop_profile_id",sa.String(36),sa.ForeignKey("crop_profiles.id")),sa.Column("map_zone",sa.String(120)),sa.Column("entry_date",sa.DateTime(timezone=True),nullable=False),sa.Column("growth_stage",sa.String(80)),sa.Column("entry_text",sa.Text(),nullable=False),sa.Column("user_question",sa.Text()),sa.Column("ai_response",sa.Text()),sa.Column("concern_level",sa.String(30),nullable=False),sa.Column("detected_topics",sa.JSON(),nullable=False),sa.Column("recommended_next_action",sa.Text()),sa.Column("follow_up_date",sa.DateTime(timezone=True)),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_diary_entries_user_id","diary_entries",["user_id"])
    op.create_index("ix_diary_entries_plan_id","diary_entries",["plan_id"])

def downgrade():
    op.drop_table("diary_entries")
    op.drop_table("refresh_tokens")
    op.drop_table("saved_plans")
    op.drop_table("crop_profiles")
    op.drop_table("species")
    op.drop_table("users")
