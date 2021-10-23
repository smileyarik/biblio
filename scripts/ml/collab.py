import argparse
import pickle

from lightfm import LightFM
from lightfm.data import Dataset
from scipy.sparse import save_npz
from sklearn.base import clone
from tqdm import tqdm

from util import read_jsonl


class LightFMResizable(LightFM):
    """A LightFM that resizes the model to accomodate new users,
    items, and features"""

    def fit_partial(
        self,
        interactions,
        user_features=None,
        item_features=None,
        sample_weight=None,
        epochs=1,
        num_threads=1,
        verbose=False,
    ):
        try:
            self._check_initialized()
            self._resize(interactions, user_features, item_features)
        except ValueError:
            # This is the first call so just fit without resizing
            pass

        super().fit_partial(
            interactions,
            user_features,
            item_features,
            sample_weight,
            epochs,
            num_threads,
            verbose,
        )

        return self

    def _resize(self, interactions, user_features=None, item_features=None):
        """Resizes the model to accommodate new users/items/features"""

        no_components = self.no_components
        no_user_features, no_item_features = interactions.shape  # default

        if hasattr(user_features, "shape"):
            no_user_features = user_features.shape[-1]
        if hasattr(item_features, "shape"):
            no_item_features = item_features.shape[-1]

        if (
            no_user_features == self.user_embeddings.shape[0]
            and no_item_features == self.item_embeddings.shape[0]
        ):
            return self

        new_model = clone(self)
        new_model._initialize(no_components, no_item_features, no_user_features)

        # update all attributes from self._check_initialized
        for attr in (
            "item_embeddings",
            "item_embedding_gradients",
            "item_embedding_momentum",
            "item_biases",
            "item_bias_gradients",
            "item_bias_momentum",
            "user_embeddings",
            "user_embedding_gradients",
            "user_embedding_momentum",
            "user_biases",
            "user_bias_gradients",
            "user_bias_momentum",
        ):
            # extend attribute matrices with new rows/cols from
            # freshly initialized model with right shape
            old_array = getattr(self, attr)
            old_slice = [slice(None, i) for i in old_array.shape]
            new_array = getattr(new_model, attr)
            new_array[tuple(old_slice)] = old_array
            setattr(self, attr, new_array)

        return self


def read_matrix(actions):
    datum = list()
    users = set()
    items = set()
    for a in tqdm(actions):
        user_id = a["user_id"]
        item_id = a["item_scf"]
        datum.append((user_id, item_id))
        users.add(user_id)
        items.add(item_id)
    dataset = Dataset()
    dataset.fit(list(users), list(items))
    actions_matrix = dataset.build_interactions(datum)[0]
    return dataset, actions_matrix


def main(
    input_directory,
    train_actions_path,
    output_dataset_path,
    output_actions_path,
    output_model_path
):
    train_actions = read_jsonl(os.path.join(input_directory, train_actions_path))
    dataset, dataset_actions = read_matrix(train_actions)
    with open(os.path.join(input_directory, output_dataset_path), "wb") as f:
        pickle.dump(dataset, f)
    save_npz(os.path.join(input_directory, output_actions_path), dataset_actions)

    collab_model = LightFMResizable(no_components=64, loss="warp")
    collab_model.fit(dataset_actions, epochs=30, num_threads=2)
    with open(os.path.join(input_directory, output_model_path), "wb") as f:
        pickle.dump(collab_model, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=str, required=True)
    parser.add_argument("--train-actions-path", type=str, required=True)
    parser.add_argument("--output-dataset-path", type=str, required=True)
    parser.add_argument("--output-actions-path", type=str, required=True)
    parser.add_argument("--output-model-path", type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
