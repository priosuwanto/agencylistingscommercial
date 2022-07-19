USE [Remap_Local]
GO

/****** Object:  Table [dbo].[AgenciesCommercial]    Script Date: 17/07/2022 19:40:48 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[AgenciesCommercial](
	[name] [varchar](50) NULL,
	[url] [varchar](max) NULL,
	[agent_count] [varchar](50) NULL,
	[market_count] [varchar](50) NULL,
	[brisbane_council_markets] [varchar](50) NULL,
	[brisbane_council_markets_percent] [varchar](50) NULL,
	[state] [varchar](50) NULL,
	[markets] [varchar](1000) NULL,
	[source] [varchar](50) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO


