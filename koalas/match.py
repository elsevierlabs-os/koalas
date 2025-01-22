from .wordframe import WordFrame
from .merge_operations import match


def match_labels(df1, df2, steps, df1_metadata, df2_metadata, df1_keep_all=True, df2_keep_all=True):
    ''' Takes two dataframe as input and matches a label column in one to
        a label column in the other.

        Parameters:
          - df1, df2: two pandas DataFrames
          - steps: list of strings with names of methods to call for the
            stepwise matching
          - df1_metadata, df1_metadata: respective metadata for the two
            DataFrames as a dictionary with the following entries:
              - name (optional): string that serves as name
              - source (optional): string with provenance information
              - labelColumn (required): name of the column containing
                the labels that are to be matched
              - conceptColumn (optional): UID of the concept (not the label)
          - df1_keep_all, df2_keep_all: if `True` the respective non-
            matched labels are returned as well

        Returns:
          - one dataframe with the matched entries and all of the original
            columns plus: a column `matched_how` that after which step the
            strings matched and a column `matched_string` that contains
            the actually matched string.
    '''

    # make WordFrames of the DataFrames, make deep copy to preserve original
    df1 = WordFrame(df1.copy(deep=True))
    df2 = WordFrame(df2.copy(deep=True))

    df1_labelCol = df1_metadata['labelColumn']
    df2_labelCol = df2_metadata['labelColumn']
    df1_name = df1_metadata.get('name', 'base')
    df2_name = df2_metadata.get('name', 'query')

    # Check upfront if all matching steps are actually available
    for step in steps:
        method = ((step[0] if type(step) is tuple else step)
                      .replace('str.', '')
                      .replace('right ', '')
                      .replace('left ', '')
                 )
        if not getattr(df1, method, False):
            raise KeyError('The step "%s" is not defined' % method)

    # The name of the label columns after matching, to group on
    df1_groupCol = '%s_%s'%(df1_labelCol, df1_name)
    df2_groupCol = '%s_%s'%(df2_labelCol, df2_name)

    matched_labels = (match(df1, df2, steps,
                      left_on=df1_labelCol, right_on=df2_labelCol,
                      left_suff=df1_name, right_suff=df2_name,
                      left_all=df1_keep_all, right_all=df2_keep_all,
                      left_drop_matched=False, right_drop_matched=False)
                      .sort_values(by='matched_how')
                     )

    return matched_labels

def match_concepts(matched_labels, df1_metadata, df2_metadata, one_to_one=True):

    conceptCol_df1 = df1_metadata['conceptColumn'] + '_' + df1_metadata['name']
    conceptCol_df2 = df2_metadata['conceptColumn'] + '_' + df2_metadata['name']
    conceptCols = [conceptCol_df1, conceptCol_df2]

    matched_concepts = (matched_labels.dropna(subset=conceptCols)
                                      .groupby(conceptCols, sort=False)
                                      .size()
                                      .to_frame(name='# label matches')
                                      .reset_index()
                       )
    if one_to_one:
        result = (matched_concepts.groupby(conceptCol_df1, sort=False)
                                  .agg({conceptCol_df2: [len, lambda x: x.head(1)],
                                       '# label matches': lambda x: x.head(1)})
                                  .reset_index()
                                  .groupby((conceptCol_df2, '<lambda>'))
                                  .agg({conceptCol_df1: [len, lambda x: x.head(1)],
                                        (conceptCol_df2, 'len'): lambda x: x.head(1),
                                       ('# label matches', '<lambda>'): lambda x: x.head(1)})
                                  .reset_index()
                 )
        result.columns = [conceptCol_df2, '# of %s'%conceptCol_df1, conceptCol_df1, '# of %s'%conceptCol_df2, '# label matches']
        result = result[[conceptCol_df1, conceptCol_df2, '# of %s'%conceptCol_df1, '# of %s'%conceptCol_df2, '# label matches']]
        duplicates_df1 = (matched_labels
                        [~matched_labels[conceptCol_df1].isin(result[conceptCol_df1])
                         & matched_labels[conceptCol_df1].notna() & matched_labels[conceptCol_df2].notna()]
                        .groupby(conceptCol_df1, sort=False)
                        .size()
                        .to_frame(name='number of labels')
                        .reset_index()
                        .rename(columns={conceptCol_df1: df1_metadata['conceptColumn']})
                      )
        duplicates_df2 = (matched_labels
                        [~matched_labels[conceptCol_df2].isin(result[conceptCol_df2])
                         & matched_labels[conceptCol_df1].notna() & matched_labels[conceptCol_df2].notna()]
                        .groupby(conceptCol_df2, sort=False)
                        .size()
                        .to_frame(name='number of labels')
                        .reset_index()
                        .rename(columns={conceptCol_df2: df2_metadata['conceptColumn']})
                      )
    else:
        result = matched_concepts
        duplicates_df1, duplicates_df2 = [], []

    orphans_df1 = (matched_labels[matched_labels[conceptCol_df2].isna()]
                    .groupby(conceptCol_df1, sort=False)
                    .size()
                    .to_frame(name='number of labels')
                    .reset_index()
                    .rename(columns={conceptCol_df1: df1_metadata['conceptColumn']})
                  )
    orphans_df2 = (matched_labels[matched_labels[conceptCol_df1].isna()]
                    .groupby(conceptCol_df2, sort=False)
                    .size()
                    .to_frame(name='number of labels')
                    .reset_index()
                    .rename(columns={conceptCol_df2: df2_metadata['conceptColumn']})
                  )

    return result, duplicates_df1, duplicates_df2, orphans_df1, orphans_df2
